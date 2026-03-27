import json
import asyncio
import asyncssh
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Node

logger = logging.getLogger(__name__)


class NodeTerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.user = self.scope.get("user")
        self.node_id = self.scope.get("url_route", {}).get("kwargs", {}).get("node_id")

        if not (self.user and self.user.is_authenticated):
            await self.close()
            return

        try:
            self.node = await Node.objects.select_related("cluster__user").aget(
                id=self.node_id
            )
            if self.node.cluster.user != self.user:
                await self.close()
                return
        except Node.DoesNotExist:
            await self.close()
            return

        await self.accept()

        self.ssh_conn = None
        self.ssh_channel = None
        self.ssh_task = None

        self.term_cols = 80
        self.term_rows = 24

        self.ssh_task = asyncio.create_task(self.start_ssh_session())

    async def disconnect(self, close_code) -> None:
        if self.ssh_task:
            self.ssh_task.cancel()

            try:
                await self.ssh_task
            except asyncio.CancelledError:
                pass

        if self.ssh_conn:
            self.ssh_conn.close()
            await self.ssh_conn.wait_closed()

        await self.close()

    async def receive(self, text_data) -> None:
        text_data_json = json.loads(text_data)
        input_data = text_data_json.get("data")
        resize_data = text_data_json.get("resize")

        if resize_data:
            self.term_cols = resize_data.get("cols", 80)
            self.term_rows = resize_data.get("rows", 24)

            if self.ssh_channel:
                try:
                    self.ssh_channel.set_terminal_size(self.term_cols, self.term_rows)
                except Exception as e:
                    logger.error(f"Failed to resize terminal: {e}")

        if input_data and self.ssh_channel:
            try:
                self.ssh_channel.write(input_data)
            except Exception as e:
                logger.error(f"Failed to write to SSH channel: {e}")

    async def start_ssh_session(self) -> None:
        try:
            logger.error("--- DEBUG NODE ---")
            logger.error(f"UUID: {self.node.id}")
            logger.error(f"Hostname: {self.node.hostname}")
            logger.error(
                f"Username in DB: '{self.node.username}' (Type: {type(self.node.username)})"
            )

            self.ssh_conn = await asyncssh.connect(
                self.node.ip_address,
                port=self.node.port,
                username=self.node.username,
                password=self.node.password,
                known_hosts=None,
                connect_timeout=10,
            )

            (
                self.ssh_stdin,
                self.ssh_stdout,
                self.ssh_stderr,
            ) = await self.ssh_conn.open_session(
                term_type="xterm-256color", term_size=(self.term_cols, self.term_rows)
            )

            self.ssh_channel = self.ssh_stdout.channel

            while True:
                data = await self.ssh_stdout.read(1024)
                if not data:
                    break
                await self.send(text_data=json.dumps({"output": data}))

            await self.close()

        except Exception as e:
            logger.error(f"SSH connection error for node {self.node.hostname}: {e}")
            await self.send(
                text_data=json.dumps(
                    {"output": "\r\n\x1b[31mSSH Error: Connection failed.\x1b[0m\r\n"}
                )
            )
            await self.close()
