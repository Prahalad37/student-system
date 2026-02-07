from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from ..models import Member, TransportRoute, StudentTransport, TransportZone, TransportStop
from ..utils import get_current_school
from ..utils.role_guards import require_roles

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def transport_home(request):
    school = get_current_school(request)
    routes = TransportRoute.objects.filter(school=school)
    transport_students = StudentTransport.objects.select_related('student', 'route').filter(school=school)
    assigned_ids = transport_students.values_list('student_id', flat=True)
    available_students = Member.objects.filter(school=school).exclude(id__in=assigned_ids)
    zones = TransportZone.objects.filter(school=school).order_by('name')
    stops = TransportStop.objects.filter(school=school).select_related('zone').order_by('zone__name', 'name')

    context = {
        'routes': routes, 'transport_students': transport_students,
        'students': available_students, 'total_buses': routes.count(),
        'students_on_bus': transport_students.count(),
        'total_revenue': transport_students.aggregate(Sum('monthly_fee'))['monthly_fee__sum'] or 0,
        'zones': zones,
        'stops': stops,
    }
    return render(request, 'transport.html', context)

@login_required
@require_roles("OWNER", "ADMIN")
def add_route(request):
    if request.method == "POST":
        TransportRoute.objects.create(
            school=get_current_school(request),
            route_name=request.POST.get('route_name'),
            vehicle_number=request.POST.get('vehicle_number'),
            driver_name=request.POST.get('driver_name'),
            driver_phone=request.POST.get('driver_phone')
        )
    return redirect('transport_home')

@login_required
@require_roles("OWNER", "ADMIN", "STAFF")
def transport_assign(request):
    if request.method == "POST":
        school = get_current_school(request)
        student = get_object_or_404(Member, id=request.POST.get('student_id'), school=school)
        route = get_object_or_404(TransportRoute, id=request.POST.get('route_id'), school=school)

        billing_mode = request.POST.get('billing_mode') or 'Manual'
        zone_id = request.POST.get('zone_id')
        stop_id = request.POST.get('stop_id')
        zone = None
        stop = None
        if zone_id and str(zone_id).isdigit():
            zone = get_object_or_404(TransportZone, id=int(zone_id), school=school)
        if stop_id and str(stop_id).isdigit():
            stop = get_object_or_404(TransportStop, id=int(stop_id), school=school)

        monthly_fee = Decimal(str(request.POST.get('monthly_fee') or '0'))
        if billing_mode in {'Zone', 'Stop', 'Hybrid'}:
            monthly_fee = Decimal('0')
            if billing_mode in {'Zone', 'Hybrid'} and zone:
                monthly_fee += Decimal(zone.base_monthly_fee or 0)
            if billing_mode in {'Stop', 'Hybrid'} and stop:
                monthly_fee += Decimal(stop.monthly_surcharge or 0)
        
        StudentTransport.objects.update_or_create(
            school=get_current_school(request), student=student,
            defaults={
                'route': route,
                'pickup_point': request.POST.get('pickup_point'),
                'billing_mode': billing_mode,
                'zone': zone,
                'stop': stop,
                'monthly_fee': monthly_fee,
            }
        )
        student.transport_mode = 'School Bus'; student.route_name = route.route_name; student.save()
    return redirect('transport_home')