from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Data export started.")

        def render_field(field):
          if field is None:
            return None
          else:
            return str(field)

        file = "UNIT_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = Unit.objects.all()
          
        data = [{
          "name": item.name, 
          "location": render_field(item.location), 
          "parent": str(item.parent), 
          "major_formation": str(item.major_formation), 
          "is_formation": item.is_formation,
          "is_major": item.is_major,
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "COMMUNICATIONMEANS_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = CommunicationMeans.objects.all()
        data = [{
          "name": item.name, 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

#################################################################

        def render_string(to_return):
          if not to_return == "":
            return to_return
          return None

        file = "CUSTOMUSER_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = CustomUser.objects.all()
        data = [{
          "username": item.username, 
          "password": "kwdikos1!",
          "first_name": render_string(str(item.first_name)),
          "last_name": render_string(str(item.last_name)),
          "unit": str(item.unit), 
          "phone": item.phone, 
          "email": render_string(str(item.email)),
          "means": render_string(",".join(str(j) for j in item.means.all())),
          "admin": item.is_admin(),
          "manager": item.is_manager(),
          "dispatcher": item.is_dispatcher(),
          "ddb": item.is_ddb(),
          "simple_user": item.is_simple_user(),
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "NETWORKSPEED_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = NetworkSpeed.objects.all()
        data = [{
          "name": item.name, 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "ROUTING_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = Routing.objects.all()
        data = [{
          "name": item.name, 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "DIGCONNECTION_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = DigConnection.objects.all()
        data = [{
          "number": item.number, 
          "name": item.name, 
          "formation_from": str(item.formation_from), 
          "unit_from": str(item.unit_from), 
          "formation_to": str(item.formation_to), 
          "unit_to": str(item.unit_to), 
          "speed": render_field(item.speed), 
          "means": str(item.means), 
          "route": str(item.route), 
          "external": item.external, 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "PYRSEIASERVER_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = PyrseiaServer.objects.all()
        data = [{
          "name": item.name, 
          "formation": str(item.formation), 
          "unit": str(item.unit),
          "domain": item.domain, 
          "exchange": item.exchange, 
          "esxi": str(item.esxi), 
          "default_gateway": str(item.default_gateway), 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "BROADBANDTRANSCEIVER_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = BroadbandTransceiver.objects.all()
        data = [{
          "hostname": item.hostname, 
          "coupling": render_field(item.coupling), 
          "coupling_code": render_field(item.coupling_code),
          "model": render_field(item.model), 
          "formation": str(item.formation), 
          "unit_from": str(item.unit_from), 
          "unit_to": render_field(item.unit_to), 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "SATELLITENODE_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = SatelliteNode.objects.all()
        data = [{
          "name": item.name, 
          "unit": str(item.unit), 
          "formation": str(item.formation), 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "HERMESNODE_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = HermesNode.objects.all()
        data = [{
          "number": item.number, 
          "location": item.location, 
          "node_type": item.node_type,
          "formation": str(item.formation), 
          "unit": str(item.unit), 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "HERMESCONNECTION_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = HermesConnection.objects.all()
        data = [{
          "number": item.number, 
          "node_from": str(item.node_from),
          "node_to": str(item.node_to),
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "HARPCORRESPONDENT_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = HarpCorrespondent.objects.all()
        data = [{
          "correspondent": item.correspondent, 
          "formation": str(item.formation),
          "unit": str(item.unit),
          "number": item.number,
          "device_type": item.device_type,
          "is_track_harp": item.is_track_harp,
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

################################################################

        file = "FAILURETYPE_EXPORT.xlsx"
        file_path = "~/Documents/" + file
        querySet = FailureType.objects.all()
        data = [{
          "means": render_field(item.means), 
          "name": item.name, 
        } for item in querySet]
        df = pd.DataFrame(data)
        df.to_excel(file_path)
        print(f"File '{file}' was successfully created.")

        print("Data export is now complete.")
