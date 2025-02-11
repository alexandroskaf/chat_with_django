from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os
from django.db.models import Q

from helpdesk_app.models import *
import pandas as pd

class Command(BaseCommand):
    help = 'Import all failure types from the "FAILURETYPE_EXPORT.xlsx" file.'

    def handle(self, *args, **options):
      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new failure types.")

      file = "FAILURETYPE_EXPORT.xlsx"
      # file = "test_failuretypes.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        means_input = render_field(str(df.iat[i, 0]).strip())
        if (not means_input is None) and (not CommunicationMeans.objects.filter(name=means_input).exists()):
          print(f"There is no communication means called '{means_input}', aborting...")
        else:
          if not means_input is None:
            means = CommunicationMeans.objects.get(name=means_input)
          else:
            means = None
          name = str(df.iat[i, 1]).strip()
          if FailureType.objects.filter(Q(means=means) & Q(name=name)).exists():
            if means is None:
              print(f"A duplicate general failure type was found, skipping...")
            else:
              print(f"A duplicate failure type for '{means}' was found, skipping...")
          else:
            FailureType(
              means = means,
              name = name
            ).save()
            if means is None:
              print(f"General failure type '{name}' was successfully created.")
            else:
              print(f"The failure type '{name}' for '{means}' was successfully created.")
      
      print("The database was successfully updated, all new communication means have now been created.")
