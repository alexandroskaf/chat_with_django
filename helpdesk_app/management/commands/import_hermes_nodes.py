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
      help = 'Import all hermes nodes from the "HERMESNODE_EXPORT.xlsx" file.'

      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new hermes nodes.")

      file = "HERMESNODE_EXPORT.xlsx"
      # file = "test_hermes_nodes.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3, 4, 5]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        number = render_field(str(df.iat[i, 0]))
        if number is None:
          print("A hermes node had no 'number' provided, aborting...")
        elif HermesNode.objects.filter(number=number).exists():
          print(f"A duplicate hermes node with the number {number} was found, skipping...")

        else:
          location = render_field(str(df.iat[i, 1]))
          node_type = render_field(str(df.iat[i, 2]))
          formation_input = render_field(str(df.iat[i, 3]))
          unit_input = render_field(str(df.iat[i, 4]))

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

          new_hermes_node = HermesNode(
            number = number,
            location = location,
            node_type = node_type,
            formation = formation,
            unit = unit,
          )
          new_hermes_node.save()
          print(f"The hermes node '{new_hermes_node}' was successfully created.")

      print("The database was successfully updated, all new hermes nodes have now been created.")
