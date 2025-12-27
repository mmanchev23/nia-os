from uuid import UUID

from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

from config.middlewares.htmx import HttpRequest

from .dtos import JobDTO
from .forms import JobForm
from .models import ScheduledJob
from .services import JobService


@login_required
def jobs(request: HttpRequest) -> HttpResponse:
    jobs = JobService.list(request.user)

    paginator = Paginator(jobs, 10)
    page_object = paginator.get_page(request.GET.get("page"))

    context = {
        "jobs": page_object,
    }

    if request.htmx and not request.htmx.target == "job-dialog":
        return render(request, "automation/jobs.html#job-table", context)

    return render(request, "automation/jobs.html", context)


@login_required
def job_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = JobForm(request.user, request.POST)

        if form.is_valid():
            if form.cleaned_data["target_node"]:
                t_type = "node"
                t_id = form.cleaned_data["target_node"].id
            else:
                t_type = "cluster"
                t_id = form.cleaned_data["target_cluster"].id

            data = JobDTO(
                user=request.user,
                name=form.cleaned_data["name"],
                command=form.cleaned_data["command"],
                schedule_type=form.cleaned_data["schedule_type"],
                minutes=form.cleaned_data["minutes"],
                target_type=t_type,
                target_id=t_id,
            )

            try:
                JobService.create(data)
                messages.success(request, "Job scheduled successfully!")

                jobs = JobService.list(request.user)
                context = {"jobs": Paginator(jobs, 10).page(1)}

                response = render(request, "automation/jobs.html#job-table", context)
                response["HX-Retarget"] = "#table"
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = JobForm(request.user)

    context = {"form": form, "url": request.path, "title": "Schedule New Job"}
    return render(request, "automation/jobs.html#job-form", context)


@login_required
def job_update(request: HttpRequest, job_id: UUID) -> HttpResponse:
    job = get_object_or_404(ScheduledJob, id=job_id, user=request.user)

    if request.method == "POST":
        form = JobForm(request.user, request.POST)

        if form.is_valid():
            t_type = "node" if form.cleaned_data.get("target_node") else "cluster"
            t_id = (
                form.cleaned_data.get("target_node")
                or form.cleaned_data.get("target_cluster")
            ).id

            data = JobDTO(
                user=request.user,
                name=form.cleaned_data["name"],
                command=form.cleaned_data["command"],
                schedule_type=form.cleaned_data["schedule_type"],
                minutes=form.cleaned_data["minutes"],
                target_type=t_type,
                target_id=t_id,
                repeats=-1,
            )

            try:
                JobService.update(job.id, request.user, data)
                messages.success(request, f"Job {data.name} updated!")

                jobs = JobService.list(request.user)
                context = {"jobs": Paginator(jobs, 10).page(1)}

                response = render(request, "automation/jobs.html#job-table", context)
                response["HX-Retarget"] = "#table"
                response["HX-Trigger"] = "closeModal"
                return response
            except ValidationError as e:
                form.add_error(None, e)
    else:
        initial = {
            "name": job.name,
            "command": job.command,
            "target_node": job.node,
            "target_cluster": job.cluster,
        }
        if job.schedule:
            initial["schedule_type"] = job.schedule.schedule_type
            initial["minutes"] = job.schedule.minutes
        else:
            initial["schedule_type"] = "O"

        form = JobForm(request.user, initial=initial)

    context = {"form": form, "url": request.path, "title": f"Edit {job.name}"}
    return render(request, "automation/jobs.html#job-form", context)


@login_required
def job_delete(request: HttpRequest, job_id: UUID) -> HttpResponse:
    job = get_object_or_404(ScheduledJob, id=job_id, user=request.user)

    if request.method == "DELETE":
        job.delete()
        messages.success(request, f"Job '{job.name}' deleted!")

        jobs = ScheduledJob.objects.filter(user=request.user).order_by("-created")
        context = {"jobs": Paginator(jobs, 10).page(1)}

        response = render(request, "automation/jobs.html#job-table", context)
        response["HX-Trigger"] = "closeModal"
        return response

    return render(request, "automation/jobs.html#job-delete-form", {"job": job})


@login_required
def job(request: HttpRequest, job_id: UUID) -> HttpResponse:
    job = get_object_or_404(ScheduledJob, id=job_id, user=request.user)

    executions = job.executions.all().select_related("node").order_by("-started_at")

    paginator = Paginator(executions, 15)
    page_object = paginator.get_page(request.GET.get("page"))

    context = {"job": job, "executions": page_object}

    if request.htmx:
        return render(request, "automation/job.html#history-table", context)

    return render(request, "automation/job.html", context)
