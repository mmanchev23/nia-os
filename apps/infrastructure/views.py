from uuid import UUID

from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from config.middlewares.htmx import HttpRequest

from .dtos import ClusterDTO, NodeDTO
from .forms import ClusterForm, NodeForm
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
                messages.success(request, f"{data.name} created!")

                clusters = ClusterService.list(request.user).annotate(
                    node_count=Count("nodes")
                )
                context = {"clusters": Paginator(clusters, 10).page(1)}

                response = render(
                    request, "infrastructure/clusters.html#cluster-table", context
                )
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = ClusterForm()

    context = {"form": form, "url": request.path, "title": "Create Cluster"}
    return render(request, "infrastructure/clusters.html#cluster-form", context)


@login_required
def cluster(request: HttpRequest, cluster_id: UUID) -> HttpResponse:
    cluster = ClusterService.get(cluster_id, request.user)

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
    cluster = ClusterService.get(cluster_id, request.user)

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
                messages.success(request, f"{data.name} updated!")

                clusters = ClusterService.list(request.user).annotate(
                    node_count=Count("nodes")
                )
                context = {"clusters": Paginator(clusters, 10).page(1)}

                response = render(
                    request, "infrastructure/clusters.html#cluster-table", context
                )
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = ClusterForm(instance=cluster)

    context = {"form": form, "url": request.path, "title": f"Edit {cluster.name}"}
    return render(request, "infrastructure/clusters.html#cluster-form", context)


@login_required
@require_http_methods(["DELETE"])
def cluster_delete(request: HttpRequest, cluster_id: UUID) -> HttpResponse:
    ClusterService.delete(cluster_id, request.user)
    messages.success(request, "Cluster deleted!")

    clusters = ClusterService.list(request.user)
    context = {"clusters": Paginator(clusters, 10).page(1)}

    return render(request, "infrastructure/clusters.html#cluster-table", context)


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
                messages.success(request, f"Node {data.hostname} created!")

                nodes = NodeService.list(request.user, cluster=data.cluster)
                context = {
                    "nodes": Paginator(nodes, 10).page(1),
                    "cluster": data.cluster,
                }

                response = render(
                    request, "infrastructure/cluster.html#node-table", context
                )
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        initial = {}
        cluster_id = request.GET.get("cluster_id")
        if cluster_id:
            cluster_obj = ClusterService.get(cluster_id, request.user)
            initial["cluster"] = cluster_obj

        form = NodeForm(request.user, initial=initial)

    context = {"form": form, "url": request.path, "title": "Add New Node"}
    return render(request, "infrastructure/cluster.html#node-form", context)


@login_required
def node_update(request: HttpRequest, node_id: UUID) -> HttpResponse:
    node = NodeService.get(node_id, request.user)

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
                messages.success(request, f"Node {data.hostname} updated!")

                nodes = NodeService.list(request.user, cluster=data.cluster)
                context = {
                    "nodes": Paginator(nodes, 10).page(1),
                    "cluster": data.cluster,
                }

                response = render(
                    request, "infrastructure/cluster.html#node-table", context
                )
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = NodeForm(request.user, instance=node)

    context = {"form": form, "url": request.path, "title": f"Edit {node.hostname}"}
    return render(request, "infrastructure/cluster.html#node-form", context)


@login_required
@require_http_methods(["DELETE"])
def node_delete(request: HttpRequest, node_id: UUID) -> HttpResponse:
    node = NodeService.get(node_id, request.user)
    cluster = node.cluster

    NodeService.delete(node_id, request.user)
    messages.success(request, "Node deleted!")

    nodes = NodeService.list(request.user, cluster=cluster)
    context = {"nodes": Paginator(nodes, 10).page(1), "cluster": cluster}

    return render(request, "infrastructure/cluster.html#node-table", context)


@login_required
def terminal(request: HttpRequest, node_id: UUID) -> HttpResponse:
    node = NodeService.get(node_id, request.user)
    return render(request, "infrastructure/terminal.html", {"node": node})
