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
      help = 'Import all satellite nodes from the "PYRSEIASERVER_EXPORT.xlsx" file.'

      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new satellite nodes.")

      file = "SATELLITENODE_EXPORT.xlsx"
      # file = "test_satellite_nodes.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        name = render_field(str(df.iat[i, 0]))
        if name is None:
          print("A satellite node had no 'name' provided, aborting...")
        elif SatelliteNode.objects.filter(name=name).exists():
          print(f"A duplicate satellite node with the name {name} was found, skipping...")

        else:
          formation_input = render_field(str(df.iat[i, 2]))
          unit_input = render_field(str(df.iat[i, 1]))

          formation_check = Unit.objects.filter(name=formation_input)
          if formation_check.exists():
            formation = formation_check.first()
          else:
            formation = None

          unit_check = Unit.objects.filter(name=unit_input)
          if unit_check.exists():
            unit = unit_check.first()
          else:
            unit = None

          new_satellite_node = SatelliteNode(
            name = name,
            formation = formation,
            unit = unit,
          )
          new_satellite_node.save()
          print(f"The satellite node '{new_satellite_node}' was successfully created.")

      print("The database was successfully updated, all new satellite nodes have now been created.")
