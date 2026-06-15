from uuid import UUID

from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required

from config.middlewares.htmx import HttpRequest

from .dtos import ClusterDTO, NodeDTO
from .forms import ClusterForm, NodeForm
from .models import Cluster, Node
from .services import ClusterService, NodeService


@login_required
def clusters(request: HttpRequest) -> HttpResponse:
    clusters = ClusterService.list(request.user).annotate(node_count=Count("nodes"))

    query = request.GET.get("q", "")
    if query:
        clusters = clusters.filter(name__icontains=query)

    paginator = Paginator(clusters, 10)
    page_object = paginator.get_page(request.GET.get("page"))

    context = {
        "clusters": page_object,
        "query": query,
    }

    if request.htmx and not request.htmx.target == "cluster-dialog":
        return render(request, "infrastructure/clusters.html#cluster-table", context)

    return render(request, "infrastructure/clusters.html", context)


@login_required
def cluster_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClusterForm(request.POST)

        if form.is_valid():
            data = ClusterDTO(
                user=request.user,
                name=form.cleaned_data["name"],
                summary=form.cleaned_data["summary"],
            )

            try:
                ClusterService.create(data)
                messages.success(request, _("{name} created!").format(name=data.name))

                clusters = ClusterService.list(request.user).annotate(
                    node_count=Count("nodes")
                )
                context = {"clusters": Paginator(clusters, 10).page(1)}

                response = render(
                    request, "infrastructure/clusters.html#cluster-table", context
                )
                response["HX-Retarget"] = "#table"
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = ClusterForm()

    context = {"form": form, "url": request.path, "title": _("Create Cluster")}
    return render(request, "infrastructure/clusters.html#cluster-form", context)


@login_required
def cluster(request: HttpRequest, cluster_id: UUID) -> HttpResponse:
    try:
        cluster = ClusterService.get(cluster_id, request.user)
    except Cluster.DoesNotExist:
        messages.error(request, _("Cluster not found."))
        clusters = ClusterService.list(request.user).annotate(node_count=Count("nodes"))
        context = {"clusters": Paginator(clusters, 10).page(1)}
        return render(request, "infrastructure/clusters.html#cluster-table", context)

    nodes = NodeService.list(request.user, cluster)

    query = request.GET.get("q", "")
    if query:
        nodes = nodes.filter(hostname__icontains=query)

    paginator = Paginator(nodes, 10)
    page_object = paginator.get_page(request.GET.get("page"))

    context = {
        "cluster": cluster,
        "nodes": page_object,
        "query": query,
    }

    if request.htmx:
        return render(request, "infrastructure/cluster.html#node-table", context)

    return render(request, "infrastructure/cluster.html", context)


@login_required
def cluster_update(request: HttpRequest, cluster_id: UUID) -> HttpResponse:
    try:
        cluster = ClusterService.get(cluster_id, request.user)
    except Cluster.DoesNotExist:
        messages.error(request, _("Cluster not found."))
        clusters = ClusterService.list(request.user).annotate(node_count=Count("nodes"))
        context = {"clusters": Paginator(clusters, 10).page(1)}
        response = render(
            request, "infrastructure/clusters.html#cluster-table", context
        )
        response["HX-Trigger"] = "closeModal"
        return response

    if request.method == "POST":
        form = ClusterForm(request.POST, instance=cluster)

        if form.is_valid():
            data = ClusterDTO(
                user=request.user,
                name=form.cleaned_data["name"],
                summary=form.cleaned_data["summary"],
            )

            try:
                ClusterService.update(cluster.id, data)
                messages.success(request, _("{name} updated!").format(name=data.name))

                clusters = ClusterService.list(request.user).annotate(
                    node_count=Count("nodes")
                )
                context = {"clusters": Paginator(clusters, 10).page(1)}

                response = render(
                    request, "infrastructure/clusters.html#cluster-table", context
                )
                response["HX-Retarget"] = "#table"
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = ClusterForm(instance=cluster)

    context = {
        "form": form,
        "url": request.path,
        "title": _("Edit {name}").format(name=cluster.name),
    }
    return render(request, "infrastructure/clusters.html#cluster-form", context)


@login_required
def cluster_delete(request: HttpRequest, cluster_id: UUID) -> HttpResponse:
    try:
        cluster = ClusterService.get(cluster_id, request.user)
    except Cluster.DoesNotExist:
        messages.error(request, _("Cluster not found."))
        return HttpResponse(status=404)

    if request.method == "DELETE":
        ClusterService.delete(cluster_id, request.user)
        messages.success(
            request, _("Cluster '{name}' deleted!").format(name=cluster.name)
        )

        clusters = ClusterService.list(request.user).annotate(node_count=Count("nodes"))
        context = {"clusters": Paginator(clusters, 10).page(1)}

        response = render(
            request, "infrastructure/clusters.html#cluster-table", context
        )

        response["HX-Trigger"] = "closeModal"
        return response

    return render(
        request,
        "infrastructure/clusters.html#cluster-delete-form",
        {"cluster": cluster},
    )


@login_required
def nodes(request: HttpRequest) -> HttpResponse:
    nodes = (
        Node.objects.filter(cluster__user=request.user)
        .select_related("cluster")
        .order_by("-created")
    )

    query = request.GET.get("q", "")
    if query:
        nodes = nodes.filter(hostname__icontains=query)

    paginator = Paginator(nodes, 10)
    page_object = paginator.get_page(request.GET.get("page"))

    context = {
        "nodes": page_object,
        "query": query,
    }

    if request.htmx and not request.htmx.target == "node-dialog":
        return render(request, "infrastructure/nodes.html#node-table", context)

    return render(request, "infrastructure/nodes.html", context)


def _render_node_table(request, cluster=None) -> HttpResponse:
    current_url = request.headers.get("HX-Current-URL", "")

    if "nodes" in current_url:
        nodes_qs = (
            Node.objects.filter(cluster__user=request.user)
            .select_related("cluster")
            .order_by("-created")
        )
        context = {"nodes": Paginator(nodes_qs, 10).page(1)}
        return render(request, "infrastructure/nodes.html#node-table", context)
    else:
        if not cluster:
            return HttpResponse(status=204)

        nodes_qs = NodeService.list(request.user, cluster=cluster)
        context = {"nodes": Paginator(nodes_qs, 10).page(1), "cluster": cluster}
        return render(request, "infrastructure/cluster.html#node-table", context)


@login_required
def node(request: HttpRequest, node_id: UUID) -> HttpResponse:
    try:
        node = NodeService.get(node_id, request.user)
    except Node.DoesNotExist:
        messages.error(request, _("Node not found."))
        return redirect("clusters")

    host = request.build_absolute_uri("/")[:-1]
    agent_url = f"{host}/static/agent.py"
    ingest_url = f"{host}/monitoring/api/ingest/"
    install_cmd = f"nohup bash -c 'curl -s {agent_url} | python3 - {ingest_url} {node.agent_key}' > /dev/null 2>&1 &"
    remove_cmd = f'pkill -f "{host}/monitoring/api/ingest/"'
    context = {
        "node": node,
        "install_cmd": install_cmd,
        "remove_cmd": remove_cmd,
    }

    return render(request, "infrastructure/node.html", context)


@login_required
def node_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NodeForm(request.user, request.POST)

        if form.is_valid():
            data = NodeDTO(
                cluster=form.cleaned_data["cluster"],
                hostname=form.cleaned_data["hostname"],
                ip_address=form.cleaned_data["ip_address"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                port=form.cleaned_data["port"],
            )

            try:
                NodeService.create(data)
                messages.success(
                    request,
                    _("Node {hostname} created!").format(hostname=data.hostname),
                )

                response = _render_node_table(request, cluster=data.cluster)
                response["HX-Retarget"] = "#table"
                response["HX-Trigger"] = "closeModal"
                return response

            except ValidationError as e:
                form.add_error(None, e)
    else:
        initial = {}
        cluster_id = request.GET.get("cluster_id")
        if cluster_id:
            try:
                cluster_obj = ClusterService.get(cluster_id, request.user)
                initial["cluster"] = cluster_obj
            except Cluster.DoesNotExist:
                pass
        form = NodeForm(request.user, initial=initial)

    template = (
        "infrastructure/nodes.html"
        if "nodes" in request.path
        else "infrastructure/cluster.html"
    )
    context = {"form": form, "url": request.path, "title": _("Add New Node")}

    return render(request, f"{template}#node-form", context)


@login_required
def node_update(request: HttpRequest, node_id: UUID) -> HttpResponse:
    try:
        node = NodeService.get(node_id, request.user)
    except Node.DoesNotExist:
        messages.error(request, _("Node not found."))
        return HttpResponse(status=404)

    if request.method == "POST":
        form = NodeForm(request.user, request.POST, instance=node)

        if form.is_valid():
            data = NodeDTO(
                cluster=form.cleaned_data["cluster"],
                hostname=form.cleaned_data["hostname"],
                ip_address=form.cleaned_data["ip_address"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                port=form.cleaned_data["port"],
            )

            try:
                NodeService.update(node.id, request.user, data)
                messages.success(
                    request,
                    _("Node {hostname} updated!").format(hostname=data.hostname),
                )

                response = _render_node_table(request, cluster=data.cluster)
                response["HX-Retarget"] = "#table"
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = NodeForm(request.user, instance=node)

    current_url = request.headers.get("HX-Current-URL", "")
    template = (
        "infrastructure/nodes.html"
        if "nodes" in current_url
        else "infrastructure/cluster.html"
    )

    context = {
        "form": form,
        "url": request.path,
        "title": _("Edit {hostname}").format(hostname=node.hostname),
    }
    return render(request, f"{template}#node-form", context)


@login_required
def node_delete(request: HttpRequest, node_id: UUID) -> HttpResponse:
    try:
        node = NodeService.get(node_id, request.user)
    except Node.DoesNotExist:
        messages.error(request, _("Node not found."))
        return HttpResponse(status=404)

    cluster = node.cluster

    if request.method == "DELETE":
        NodeService.delete(node_id, request.user)
        messages.success(
            request, _("Node '{hostname}' deleted!").format(hostname=node.hostname)
        )

        response = _render_node_table(request, cluster=cluster)
        response["HX-Trigger"] = "closeModal"
        return response

    current_url = request.headers.get("HX-Current-URL", "")
    template = (
        "infrastructure/nodes.html"
        if "nodes" in current_url
        else "infrastructure/cluster.html"
    )

    return render(request, f"{template}#node-delete-form", {"node": node})


@login_required
def terminal(request: HttpRequest, node_id: UUID) -> HttpResponse:
    try:
        node = NodeService.get(node_id, request.user)
    except Node.DoesNotExist:
        messages.error(request, _("Node not found."))
        return HttpResponse(status=404)

    return render(request, "infrastructure/terminal.html", {"node": node})
