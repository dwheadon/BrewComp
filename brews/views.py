from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.utils import timezone


@login_required
def competitions(request):
    # return HttpResponse("Choose a competition.")
    today = timezone.now().date()
    comps_past = Competition.objects.filter(date__lt=today)
    comps_present = Competition.objects.filter(date=today)
    comps_future = Competition.objects.filter(date__gt=today)
    context = {
        'request': request,
        'comps_present': comps_present,  # !!! order by name?
        'comps_past': comps_past,  # !!! order newest (most recent) > oldest
        'comps_future': comps_future, # !!! order oldest > newest (furthest in future)
        
    }
    return render(request, "brews/competitions.html", context)


@login_required
def competition(request, competition_id):
    competition = Competition.objects.get(id=competition_id)
    today = timezone.now().date()
    judgement = None
    results = None
    if today >= competition.date and not competition.open:
        results = {}
        num_entries = competition.entry_set.all().count()
        num_judgements = Judgement.objects.filter(competition=competition).count()
        for entry in competition.entry_set.all():
            results[entry] = [None, {}]
            entry_total = 0
            for criterion in competition.criteria.all():
                results[entry][1][criterion] = [None, []]
                criterion_total = 0
                spread = criterion.max_points - criterion.min_points
                for rank in Rank.objects.filter(entry=entry, ranking__criterion=criterion, ranking__judgement__competition=competition):
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
        judgement = Judgement.objects.filter(competition=competition,judge=request.user).first()
    # return HttpResponse("Info, results (if complete), link to judge.")
    context = {
        'request': request,
        'judgement': judgement,
        'competition': competition,
        'results': results,
        'today': today,
    }
    return render(request, "brews/competition.html", context)


@login_required
def judgement(request, competition_id):
    competition = Competition.objects.get(id=competition_id)
    if request.method == 'POST':
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
        for criterion in competition.criteria.all():
            ranks = []
            if criterion.id not in data:
                error = "Not all criteria submitted"
                return redirect('judgement_error', competition_id=competition_id)
            else:
                for entry in competition.entry_set.all():
                    if entry.id not in data[criterion.id]:
                        error = "Rank not chosen for all criteria"
                        return redirect('judgement_error', competition_id=competition_id)
                    else:
                        ranks.append(data[criterion.id][entry.id])
            ranks.sort()
            if ranks != list(range(1, competition.entry_set.all().count()+1)):
                error = "Ranks are not unique for all criteria"
                return redirect('judgement_error', competition_id=competition_id)

        # All entries for all criteria accounted for
        # !!! crashes when attempting multiple submissions or re-submissions
        judgement = Judgement(competition=competition, judge=request.user)
        judgement.save()
        for criterion_id in data:
            ranking = Ranking(judgement=judgement, criterion_id=criterion_id)
            ranking.save()
            for entry_id in data[criterion_id]:
                rank = Rank(ranking=ranking, entry_id=entry_id, ordinal=data[criterion_id][entry_id])
                rank.save()
        return redirect('competition', competition_id=competition_id)
    else:
        context = {
            'request': request,
            'competition': competition,
        }
        return render(request, "brews/judgement.html", context)

