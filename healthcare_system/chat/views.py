from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect


def room(request, room_name):
    type_of_patient = request.GET["type"]
    name_of_patient = request.GET["name"]
    receiver = request.GET['receiver']
    print(f" list of sessions {dir(request.session)}")
    context = {'type_of_patient': type_of_patient,
               'name_of_patient': name_of_patient,
               'receiver': receiver,
               }
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name,
        'user_data': context,
    })
