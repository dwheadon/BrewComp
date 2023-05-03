from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import *
from .forms import *
from django.utils import timezone
from django.forms import modelformset_factory


def handle_access_key(request):
    if 'access' in request.GET:
        url_access_key = request.GET['access']
        request.session['access_key'] = url_access_key
    return request.session.get("access_key", "")


@login_required
def feedback(request):
    session_access_key = handle_access_key(request)
    return HttpResponse("under construction")


def home(request):
    session_access_key = handle_access_key(request)
    return render(request, "brews/home.html", {})


def unauthorized(request):
    session_access_key = handle_access_key(request)
    return render(request, "brews/unauthorized.html", {})


@login_required
def competitions(request):
    session_access_key = handle_access_key(request)

    today = timezone.now().date()
    comps_past = Competition.objects.filter(date__lt=today).filter(Q(access_key=session_access_key) | Q(access_key=None) | Q(access_key=""))
    comps_present = Competition.objects.filter(date=today).filter(Q(access_key=session_access_key) | Q(access_key=None) | Q(access_key=""))
    comps_future = Competition.objects.filter(date__gt=today).filter(Q(access_key=session_access_key) | Q(access_key=None) | Q(access_key=""))
    if request.user.is_staff:
        comps_past = Competition.objects.filter(date__lt=today)
        comps_present = Competition.objects.filter(date=today)
        comps_future = Competition.objects.filter(date__gt=today)

    form = CreateCompetitionForm()
    if request.method == "POST":
        form = CreateCompetitionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("competitions")
    context = {
        'request': request,
        'comps_present': comps_present,  # !!! order by name?
        'comps_past': comps_past,  # !!! order newest (most recent) > oldest
        'comps_future': comps_future, # !!! order oldest > newest (furthest in future)
        'form': form,       
    }
    return render(request, "brews/competitions.html", context)


@login_required
def competition(request, competition_id):
    session_access_key = handle_access_key(request)

    competition = Competition.objects.get(id=competition_id)
    if competition.access_key and not (session_access_key == competition.access_key or request.user.is_staff):
        return redirect('unauthorized')

    today = timezone.now().date()
    winners = None
    if competition.round_set.count() != 0 and competition.round_set.last().heat_set.count() != 0:
        winners = Entry.objects.filter(heats_won__in=competition.round_set.last().heat_set.all())
    entry_form = EntryForm()
    competition_form = UpdateCompetitionForm(instance=competition)
    round_form = RoundForm()
    if request.method == "POST":
        if 'submit_entry_registration' in request.POST:
            entry_form = EntryForm(request.POST)
            if entry_form.is_valid():
                entry = entry_form.save(commit=False)
                entry.competition = competition
                entry.label = competition.get_next_label()
                entry.brewer = request.user
                entry.save()
                return redirect("competition", competition_id=competition_id)
                # djw: need to be able to retract my (and only my) entries as well
        elif 'submit_competition_update' in request.POST:
            competition_form = UpdateCompetitionForm(request.POST, instance=competition)
            if competition_form.is_valid():
                competition_form.save()
                return redirect("competition", competition_id=competition_id)
        elif 'submit_new_round' in request.POST:
            round_form = RoundForm(request.POST)
            if round_form.is_valid():
                last_round = Round.objects.filter(competition=competition).last()
                round = round_form.save(commit=False)
                round.competition = competition
                round.number = competition.get_next_round()
                round.status = Competition.Status.REGISTRATION
                round.save()
                if round.number == 1:
                    round.entries.add(*competition.entry_set.all())
                else:
                    last_round_winners = Entry.objects.filter(heats_won__round=last_round)
                    round.entries.add(*last_round_winners)
                return redirect("competition", competition_id=competition_id)

    context = {
        'request': request,
        'judgement': judgement,
        'competition': competition,
        'today': today,
        'winners': winners,
        'entry_form': entry_form,
        'competition_form': competition_form,
        'round_form': round_form,
    }
    return render(request, "brews/competition.html", context)


@login_required
def round(request, round_id):
    session_access_key = handle_access_key(request)

    round = Round.objects.get(id=round_id)
    if round.competition.access_key and not (session_access_key == round.competition.access_key or request.user.is_staff):
        return redirect('unauthorized')

    winners = Entry.objects.filter(heats_won__in=round.heat_set.all())
    round_form = UpdateRoundForm(instance=round)
    heat_form = CreateHeatForm()
    if request.method == "POST":
        if 'submit_round_update' in request.POST:
            round_form = UpdateRoundForm(request.POST, instance=round)
            if round_form.is_valid():
                round_form.save()
                return redirect("round", round_id=round_id)
        elif 'submit_new_heat' in request.POST:
            heat_form = CreateHeatForm(request.POST)
            if heat_form.is_valid():
                heat = heat_form.save(commit=False)
                heat.round = round
                heat.number = round.get_next_heat()
                heat.status = Competition.Status.REGISTRATION
                heat.save()
                for criteria in round.competition.criteria.all():
                    criteria.pk = None
                    criteria.save()
                    heat.criteria.add(criteria)
                return redirect("round", round_id=round_id)

    context = {
        'request': request,
        'round': round,
        'winners': winners,
        'round_form': round_form,
        'heat_form': heat_form,
    }
    return render(request, "brews/round.html", context)


@login_required
def heat(request, heat_id):
    session_access_key = handle_access_key(request)

    heat = Heat.objects.get(id=heat_id)
    if heat.round.competition.access_key and not (session_access_key == heat.round.competition.access_key or request.user.is_staff):
        return redirect('unauthorized')
    
    my_judgement = None
    results = None
    heat_form = UpdateHeatForm(instance=heat)
    UpdateCriteriaFormSet = modelformset_factory(Criterion, form=UpdateCriterionForm, extra=0, edit_only=True)
    criteria_formset = UpdateCriteriaFormSet(queryset=heat.criteria.all())
    # Only include entries registered for this round that haven't already been selected for another heat
    heat_form.fields['entries'].queryset = Entry.objects.filter(round=heat.round) # .exclude(heats_entered__round=heat.round)
    heat_form.fields['winners'].queryset = Entry.objects.filter(heats_entered=heat) # .exclude(heats_entered__round=heat.round)
    if request.method == "POST":
        if 'submit_heat_update' in request.POST:
            heat_form = UpdateHeatForm(request.POST, instance=heat)
            if heat_form.is_valid():
                heat_form.save()
                return redirect("heat", heat_id=heat_id)
        elif 'submit_heat_criteria_update' in request.POST:
            criteria_formset = UpdateCriteriaFormSet(request.POST)
            if criteria_formset.is_valid():
                criteria_formset.save()
                return redirect("heat", heat_id=heat_id)

    if heat.status == Competition.Status.CLOSED or heat.status == Competition.Status.COMPLETE:
        results = {}
        num_entries = heat.entries.all().count()
        num_judgements = Judgement.objects.filter(heat=heat).count()
        for entry in heat.entries.all():
            results[entry] = [None, {}]
            entry_total = 0
            for criterion in heat.criteria.all():
                results[entry][1][criterion] = [None, []]
                criterion_total = 0
                spread = criterion.max_points - criterion.min_points
                for rank in Rank.objects.filter(entry=entry, ranking__criterion=criterion, ranking__judgement__heat=heat):
                    points = criterion.min_points + spread / (num_entries - 1) * (num_entries - rank.ordinal)
                    results[entry][1][criterion][1].append(points)
                    criterion_total += points
                    entry_total += points
                results[entry][1][criterion][1].sort()
                results[entry][1][criterion][1].reverse()
                results[entry][1][criterion][0] = criterion_total / num_judgements
            average = entry_total / num_judgements
            results[entry][0] = average
        results = dict(sorted(results.items(), key=lambda item: -(item[1][0])))
    if request.user.is_authenticated:
        my_judgement = Judgement.objects.filter(heat=heat,judge=request.user).first()
    judgements = None
    if request.user.is_staff:
        judgements = Judgement.objects.filter(heat=heat)
    context = {
        'request': request,
        'heat': heat,
        'heat_form': heat_form,
        'criteria_formset': criteria_formset,
        'judgements': judgements,
        'my_judgement': my_judgement,
        'results': results,
    }
    return render(request, "brews/heat.html", context)


@login_required
def judgement(request, heat_id):
    session_access_key = handle_access_key(request)

    heat = Heat.objects.get(id=heat_id)
    if heat.round.competition.access_key and not (session_access_key == heat.round.competition.access_key or request.user.is_staff):
        return redirect('unauthorized')
        
    if request.method == 'POST':
        judgement = Judgement.objects.filter(heat=heat, judge=request.user).first()
        if judgement:  # the user has already submitted a scorecard for this heat
            return redirect('judgement_error', heat_id=heat_id)

        error = None
        data = {}
        for key, value in request.POST.items():
            if key[:9] == "criterion":  # skip the csrf
                first_dash = key.index('-', 10)
                criterion_id = int(key[10:first_dash])
                second_dash = key.index('-', first_dash+1)
                entry_id = int(key[second_dash+1:])
                if criterion_id not in data:
                    data[criterion_id] = {}
                data[criterion_id][entry_id] = int(value)
        # Verify we have all the data
        for criterion in heat.criteria.all():
            ranks = []
            if criterion.id not in data:
                error = "Not all criteria submitted"
                return redirect('judgement_error', heat_id=heat_id)
            else:
                for entry in heat.entries.all():
                    if entry.id not in data[criterion.id]:
                        error = "Rank not chosen for all criteria"
                        return redirect('judgement_error', heat_id=heat_id)
                    else:
                        ranks.append(data[criterion.id][entry.id])
            ranks.sort()
            if ranks != list(range(1, heat.entries.all().count()+1)):
                error = "Ranks are not unique for all criteria"
                return redirect('judgement_error', heat_id=heat_id)

        # All entries for all criteria accounted for
        # !!! crashes when attempting multiple submissions or re-submissions
        judgement = Judgement(heat=heat, judge=request.user)
        judgement.save()
        for criterion_id in data:
            ranking = Ranking(judgement=judgement, criterion_id=criterion_id)
            ranking.save()
            for entry_id in data[criterion_id]:
                rank = Rank(ranking=ranking, entry_id=entry_id, ordinal=data[criterion_id][entry_id])
                rank.save()
        return redirect('heat', heat_id=heat_id)
    else:
        context = {
            'request': request,
            'heat': heat,
        }
        return render(request, "brews/judgement.html", context)


@login_required
def judgement_error(request, heat_id):
    session_access_key = handle_access_key(request)

    heat = Heat.objects.get(id=heat_id)
    if heat.round.competition.access_key and not (session_access_key == heat.round.competition.access_key or request.user.is_staff):
        return redirect('unauthorized')
    judgement = Judgement.objects.filter()

    context = {
        'request': request,
        'heat': heat,
        'judgement': judgement,
    }
    return render(request, "brews/judgement_error.html", context)


@login_required
def judgement_performance(request, heat_id):
    session_access_key = handle_access_key(request)

    heat = Heat.objects.get(id=heat_id)
    if heat.round.competition.access_key and not (session_access_key == heat.round.competition.access_key or request.user.is_staff):
        return redirect('unauthorized')
    
    judgement = Judgement.objects.filter(heat=heat, judge=request.user).first()

    context = {
        'request': request,
        'heat': heat,
        'judgement': judgement,
    }
    return render(request, "brews/judgement_performance.html", context)