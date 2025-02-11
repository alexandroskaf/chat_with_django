from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os
from django.db.models import Q

from helpdesk_app.models import *
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
      help = 'Import all digital connections from the "DIGCONNECTION_EXPORT.xlsx" file.'

      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new digital connections.")

      file = "DIGCONNECTION_EXPORT.xlsx"
    #   file = "test_dig_connections.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        number = render_field(str(df.iat[i, 0]))
        if number is None:
          print("A diginal connection had no 'number' provided, aborting...")
        elif DigConnection.objects.filter(number=number).exists():
          print(f"A duplicate digital connection with the number {number} was found, skipping...")

        else:
            name = render_field(str(df.iat[i, 1]))

            formation_from_input = render_field(str(df.iat[i, 2]).strip())
            unit_from_input = render_field(str(df.iat[i, 3]).strip())
            formation_to_input = render_field(str(df.iat[i, 4]).strip())
            unit_to_input = render_field(str(df.iat[i, 5]).strip())

            speed_input = render_field(str(df.iat[i, 6]).strip())
            means_input = render_field(str(df.iat[i, 7]).strip())
            route_input = render_field(str(df.iat[i, 8]).strip())

            external_input = df.iat[i, 9]
            if not external_input is None:
              external = external_input
            else:
              external = False

            formation_from_check = Unit.objects.filter(name=formation_from_input)
            if formation_from_check.exists():
                formation_from = formation_from_check.first()
            else:
                formation_from = None

            unit_from_check = Unit.objects.filter(name=unit_from_input)
            if unit_from_check.exists():
                unit_from = unit_from_check.first()
            else:
                unit_from = None

            formation_to_check = Unit.objects.filter(name=formation_to_input)
            if formation_to_check.exists():
                formation_to = formation_to_check.first()
            else:
                formation_to = None

            unit_to_check = Unit.objects.filter(name=unit_to_input)
            if unit_to_check.exists():
                unit_to = unit_to_check.first()
            else:
                unit_to = None

            speed_check = NetworkSpeed.objects.filter(name=speed_input)
            if speed_check.exists():
                speed = speed_check.first()
            else:
                speed = None

            means_check = CommunicationMeans.objects.filter(name=means_input)
            if means_check.exists():
                means = means_check.first()
            else:
                means = None

            route_check = Routing.objects.filter(name=route_input)
            if route_check.exists():
                route = route_check.first()
            else:
                route = None

            new_dig_connection = DigConnection(
                number = number,
                name = name,
                formation_from = formation_from,
                unit_from = unit_from,
                formation_to = formation_to,
                unit_to = unit_to,
                speed = speed,
                means = means,
                route = route,
                external = external,
            )
            new_dig_connection.save()
            print(f"The digital connection '{new_dig_connection}' was successfully created.")

      print("The database was successfully updated, all new digital connections have now been created.")

