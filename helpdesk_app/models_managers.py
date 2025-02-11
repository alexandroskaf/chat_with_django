from django.db import models
from django.db.models import Q

from .models import *



# class CommentManager(models.Manager):
#     def for_report(self, report):
#         return self.filter(report=report).order_by("-created_date")

#     def for_failure(self, failure):
#         return self.filter(failure=failure).order_by("-created_date")   
    
#     def get_last_for_report(self, report):
#         return self.filter(report=report).order_by("-created_date").first()


class FailureManager(models.Manager):
    """Failure model queries handler."""

    # DIFFERENT VIEW PERMISSIONS FOR DIFFERENT TYPES OF USERS
    def get_filter_for_user(self, user):
        submitter_filter = Q(submitter_user=user)
        all_closed_filter = Q(status="CL")
        unit = user.unit
        unit_filter = Q(unit = user.unit) | Q(supervisor_unit = user.unit)

        # simple user - can only view failures submitted by them + failures that have already been CLOSED
        if user.is_simple_user():
            user_filter = submitter_filter | all_closed_filter | unit_filter
        elif user.is_ddb():
            if str(unit) == "ΓΕΣ":
                ddb_user_filter = ~Q(pk=None)

            else:
                if str(unit) == "1 ΣΤΡΑΤΙΑ":
                    ddb_user_filter = (
                        Q(supervisor_major_formation__name="1 ΣΤΡΑΤΙΑ") | 
                        Q(supervisor_major_formation__name="Γ ΣΣ") | 
                        Q(supervisor_major_formation__name="Δ ΣΣ")
                    )
                else:
                    ddb_user_filter = (Q(supervisor_major_formation__name=unit))

            user_filter = submitter_filter | all_closed_filter | ddb_user_filter | unit_filter

        # dispatcher - simple user permissions + anything that has been dispatched to them
        elif user.is_dispatcher():
            means = user.means.all()
            user_filter = submitter_filter | Q(means__in=means) | all_closed_filter

        else:
            # manager/admin - everything
            user_filter = ~Q(pk=None)  # always true Q - (primary key cannot be empty)     

        return user_filter

    def get_for_user(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter)

    # returns the number of ALL failures that this user HAS PERMISSION TO VIEW
    def count_all(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter).count()  

    # returns the number of NEW failures that this user has submitted
    def count_new(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter & Q(status="NE")).count()  

    # returns the number of OPEN failures that this user has submitted
    def count_open(self, user):
        user_filter = self.get_filter_for_user(user)
        # if the user is a "simple" user or "ddb", so both NEW and OPEN failures as OPEN
        if user.is_simple_user() or user.is_ddb():
            return self.filter(user_filter & (Q(status="NE") | Q(status="OP"))).count()             
        else:
            return self.filter(user_filter & Q(status="OP")).count() 

    # returns the number of failures submitted by this user that are IN PROGRESS
    def count_progress(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter & Q(status="PR")).count()  

    # returns the number of CLOSED failures that this or any other user has submitted
    def count_closed(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter, Q(status="CL")).count()        
        # return self.get_for_user(user).filter(status="CL").count()


class ReportManager(models.Manager):
    """Report model queries handler."""

    # DIFFERENT VIEW PERMISSIONS FOR DIFFERENT TYPES OF USERS
    def get_filter_for_user(self, user):
        submitter_filter = Q(submitter_user=user)
        all_closed_filter = Q(status="CL")
        unit = user.unit
        unit_filter = Q(unit = user.unit) | Q(supervisor_unit = user.unit)

        # simple user - can only view failures submitted by them + failures that have already been CLOSED
        if user.is_simple_user():
            user_filter = submitter_filter | all_closed_filter | unit_filter

        elif user.is_ddb():
            if str(unit) == "ΓΕΣ":
                ddb_user_filter = ~Q(pk=None)

            else:
                if str(unit) == "1 ΣΤΡΑΤΙΑ":
                    ddb_user_filter = (
                        Q(supervisor_major_formation__name="1 ΣΤΡΑΤΙΑ") | 
                        Q(supervisor_major_formation__name="Γ ΣΣ") | 
                        Q(supervisor_major_formation__name="Δ ΣΣ")
                    )
                else:
                    ddb_user_filter = (Q(supervisor_major_formation__name=unit))

            user_filter = submitter_filter | all_closed_filter | ddb_user_filter | unit_filter

        # dispatcher - simple user permissions + anything that has been dispatched to them
        elif user.is_dispatcher():
            means = user.means.all()
            user_filter = submitter_filter | Q(means__in=means) | all_closed_filter

        else:
            # manager/admin - everything
            user_filter = ~Q(pk=None)  # always true Q - (primary key cannot be empty)     

        return user_filter

    def get_for_user(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter)

    # returns the number of ALL failures that this user HAS PERMISSION TO VIEW
    def count_all(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter).count()  

    # returns the number of NEW failures that this user has submitted
    def count_new(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter & Q(status="NE")).count()  

    # returns the number of OPEN failures that this user has submitted
    def count_open(self, user):
        user_filter = self.get_filter_for_user(user)
        # if the user is a "simple" user or "ddb", so both NEW and OPEN failures as OPEN
        if user.is_simple_user() or user.is_ddb():
            return self.filter(user_filter & (Q(status="NE") | Q(status="OP"))).count()             
        else:
            return self.filter(user_filter & Q(status="OP")).count() 

    # returns the number of failures submitted by this user that are IN PROGRESS
    def count_progress(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter & Q(status="PR")).count()  

    # returns the number of CLOSED failures that this or any other user has submitted
    def count_closed(self, user):
        user_filter = self.get_filter_for_user(user)
        return self.filter(user_filter, Q(status="CL")).count()        
        # return self.get_for_user(user).filter(status="CL").count()


class CommunicationMeansManager(models.Manager):
    """CommunicationMeans model queries handler."""

    # SOS - MUST RESPECT USER PERMISSIONS

    # FOR FAILURES - all methods return counts from failures that the user can see
    # get all failures regarding this system
    def get_all_failures_for_user(self, user):
        return Failure.objects.get_for_user(user).filter(means=self.id)

    # count ALL failures regarding this system
    def count_all_failures(self, user):
        return self.get_all_failures_for_user(user).count()

    # count NEW failures regarding this system
    def count_new_failures(self, user):
        return self.get_all_failures_for_user(user).filter(status="NE").count()

    # count IN PROGRESS failures regarding this system
    def count_progress_failures(self, user):
        return self.get_all_failures_for_user(user).filter(status="PR").count()

    # count CLOSED failures regarding this system
    def count_closed_failures(self, user):
        return self.get_all_failures_for_user(user).filter(status="CL").count()

    # get the percentage of CLOSED / (CLOSED + IN PROGRESS) failures
    def get_closed_failures_percentage(self, user):
        not_new_count = self.get_all_failures_for_user(user).filter(not Q(status="NE")).count()
        if not_new_count != 0:
            return round(self.count_closed_failures() / not_new_count * 100)
        else:
            return 0.0

    # FOR REPORTS - IF MEANS WILL BE A FIELD OF THE NEW REPORT MODEL
    # all methods return counts from reports that the user can see
    # get all failures regarding this system
    def get_all_reports_for_user(self, user):
        return Report.objects.get_for_user(user).filter(means=self.id)

    # count ALL reports regarding this system
    def count_all_reports(self, user):
        return self.get_all_reports_for_user(user).count()

    # count NEW reports regarding this system
    def count_new_reports(self, user):
        return self.get_all_reports_for_user(user).filter(status="NE").count()

    # count IN PROGRESS reports regarding this system
    def count_progress_reports(self, user):
        return self.get_all_reports_for_user(user).filter(status="PR").count()

    # count CLOSED reports regarding this system
    def count_closed_reports(self, user):
        return self.get_all_reports_for_user(user).filter(status="CL").count()
    
    # get the percentage of CLOSED / (CLOSED + IN PROGRESS) reports
    def get_closed_reports_percentage(self, user):
        not_new_count = self.get_all_reports_for_user(user).filter(not Q(status="NE")).count()
        if not_new_count != 0:
            return round(self.count_closed_reports() / not_new_count * 100)
        else:
            return 0.0

    # ??
    def get_progress(self, user):
        dispatchers_progress_dict = {}

        if user.is_admin() or user.is_manager():
            means = self.all()
        elif user.is_dispatcher():
            means = user.means.all()
        else:
            return

        return dispatchers_progress_dict
        # for mean in means:
        #     dispatchers_progress_dict[mean.name] = {}
        #     dispatchers_progress_dict[mean.name]["id"] = mean.id
        #     dispatchers_progress_dict[mean.name][
        #         "percentage"
        #     ] = mean.get_closed_reports_percentage(user)
        #     dispatchers_progress_dict[mean.name]["closed"] = mean.count_closed_reports(user)
        #     dispatchers_progress_dict[mean.name][
        #         "all"
        #     ] = mean.get_progress_closed_reports()

        # return dispatchers_progress_dict


class UnitManager(models.Manager):
    # each user will be able to see only those units subordinate to them
    def for_user(self, user):
        user_unit = user.unit
        if str(user_unit) == "ΓΕΣ":
            return self.all()

        elif user_unit.is_major:
            if str(user_unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(major_formation__name="1 ΣΤΡΑΤΙΑ") | Q(major_formation__name="Γ ΣΣ") | Q(major_formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(major_formation=user_unit))

        # default case
        elif user_unit.is_formation:
            return self.filter(Q(parent=user_unit))


class DigConnectionManager(models.Manager):

    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(
                    Q(formation_from__name="1 ΣΤΡΑΤΙΑ") | Q(formation_from__name="Γ ΣΣ") | Q(formation_from__name="Δ ΣΣ") |
                    Q(formation_to__name="1 ΣΤΡΑΤΙΑ") | Q(formation_to__name="Γ ΣΣ") | Q(formation_to__name="Δ ΣΣ")
                )
            else:
                return self.filter(Q(formation_from=unit) | Q(formation_to=unit))

        elif unit.is_formation:
            return self.filter(Q(unit_from=unit) | Q(unit_to=unit))

    # to filter based on DIDES or EPSAD communication means
    def for_unit_and_means(self, unit, means):
        if str(unit) == "ΓΕΣ":
            return self.filter(Q(means=means))
            
        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(
                    Q(means=means) & 
                    (Q(formation_from__name="1 ΣΤΡΑΤΙΑ") | Q(formation_from__name="Γ ΣΣ") | Q(formation_from__name="Δ ΣΣ") |
                    Q(formation_to__name="1 ΣΤΡΑΤΙΑ") | Q(formation_to__name="Γ ΣΣ") | Q(formation_to__name="Δ ΣΣ"))
                )
            else:
                return self.filter(Q(means=means) & (Q(formation_from=unit) | Q(formation_to=unit)))

        elif unit.is_formation:
            return self.filter(Q(means=means) & (Q(unit_from=unit) | Q(unit_to=unit)))


    def for_unit_and_means_edit(self, unit, means, is_external):
        if not unit.is_formation:
            unit = unit.parent

        # if is_external is None, EPSAD was chosen without a circuit, so bring all EPSAD because why not
        if is_external is None:
            return self.filter(Q(means=means) & (Q(unit_from=unit) | Q(unit_to=unit)))

        # if is_external is True, we know for a fact that the means is EPSAD
        if is_external:
            return self.filter(Q(external=is_external) & (Q(unit_from=unit) | Q(unit_to=unit)))

        return self.filter(Q(external=is_external) & Q(means=means) & (Q(unit_from=unit) | Q(unit_to=unit)))


class BroadbandTransceiverManager(models.Manager):
    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(formation__name="1 ΣΤΡΑΤΙΑ") | Q(formation__name="Γ ΣΣ") | Q(formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(formation=unit))

        elif unit.is_formation:
            return self.filter(Q(unit_from=unit))


    def for_unit_edit(self, unit):
        if not unit.is_formation:
            unit = unit.parent
        return self.filter(Q(unit_from=unit))


class HermesNodeManager(models.Manager):
    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(formation__name="1 ΣΤΡΑΤΙΑ") | Q(formation__name="Γ ΣΣ") | Q(formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(formation=unit))

        elif unit.is_formation:
            return self.filter(Q(unit=unit))

    def for_unit_edit(self, unit):
        if not unit.is_formation:
            unit = unit.parent
        return self.filter(Q(unit=unit))        


class HermesConnectionManager(models.Manager):

    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(node_from__formation__name="1 ΣΤΡΑΤΙΑ") | Q(node_from__formation__name="Γ ΣΣ") | Q(node_from__formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(node_from__formation=unit))

        elif unit.is_formation:
            return self.filter(Q(node_from__unit=unit))

    def for_unit_edit(self, unit):
        if not unit.is_formation:
            unit = unit.parent
        return self.filter(Q(node_from__unit=unit))


class PyrseiaServerManager(models.Manager):
    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(formation__name="1 ΣΤΡΑΤΙΑ") | Q(formation__name="Γ ΣΣ") | Q(formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(formation=unit))

        elif unit.is_formation:
            return self.filter(Q(unit=unit))

    def for_unit_edit(self, unit):
        if not unit.is_formation:
            unit = unit.parent
        return self.filter(Q(unit=unit))


class SatelliteNodeManager(models.Manager):

    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(formation__name="1 ΣΤΡΑΤΙΑ") | Q(formation__name="Γ ΣΣ") | Q(formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(formation=unit))

        elif unit.is_formation:
            return self.filter(Q(unit=unit))

    def for_unit_edit(self, unit):
        if not unit.is_formation:
            unit = unit.parent
        return self.filter(Q(unit=unit))


class HarpCorrespondentManager(models.Manager):
    def for_unit(self, unit):
        if str(unit) == "ΓΕΣ":
            return self.all()

        elif unit.is_major:
            if str(unit) == "1 ΣΤΡΑΤΙΑ":
                return self.filter(Q(formation__name="1 ΣΤΡΑΤΙΑ") | Q(formation__name="Γ ΣΣ") | Q(formation__name="Δ ΣΣ"))
            else:
                return self.filter(Q(formation=unit))

        elif unit.is_formation:
            return self.filter(Q(unit=unit))
    
    def for_unit_edit(self, unit):
        if not unit.is_formation:
            unit = unit.parent
        return self.filter(Q(unit=unit))
