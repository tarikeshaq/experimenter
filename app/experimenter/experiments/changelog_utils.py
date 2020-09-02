from django.contrib.auth import get_user_model
from rest_framework import serializers

from experimenter.base.serializers import CountrySerializer, LocaleSerializer
from experimenter.experiments.models import (
    ExperimentCore,
    ExperimentChangeLog,
)
from experimenter.experiments.api.v1.serializers import ExperimentVariantSerializer
from experimenter.projects.serializers import ProjectSerializer


class ChangelogSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_serialized_vals = {}
        if self.instance and self.instance.id:
            self.old_serialized_vals = ChangeLogSerializer(self.instance).data

    def update_changelog(self, instance, validated_data):
        new_serialized_vals = ChangeLogSerializer(instance).data
        user = self.context["request"].user
        changed_data = validated_data.copy()
        generate_change_log(
            self.old_serialized_vals, new_serialized_vals, instance, changed_data, user
        )

        return instance


class ChangeLogSerializer(serializers.ModelSerializer):
    variants = ExperimentVariantSerializer(many=True, required=False)
    locales = LocaleSerializer(many=True, required=False)
    countries = CountrySerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)

    class Meta:
        model = ExperimentCore
        fields = (
            "addon_experiment_id",
            "addon_release_url",
            "analysis_owner",
            "analysis",
            "bugzilla_id",
            "client_matching",
            "countries",
            "data_science_issue_url",
            "design",
            "engineering_owner",
            "feature_bugzilla_url",
            "firefox_channel",
            "firefox_max_version",
            "firefox_min_version",
            "locales",
            "message_template",
            "message_type",
            "name",
            "normandy_id",
            "objectives",
            "other_normandy_ids",
            "owner",
            "platforms",
            "population_percent",
            "pref_branch",
            "pref_name",
            "pref_type",
            "profile_age",
            "projects",
            "proposed_duration",
            "proposed_enrollment",
            "proposed_start_date",
            "public_description",
            "qa_status",
            "recipe_slug",
            "related_to",
            "related_work",
            "results_changes_to_firefox",
            "results_confidence",
            "results_data_for_hypothesis",
            "results_early_end",
            "results_fail_to_launch",
            "results_failures_notes",
            "results_impact_notes",
            "results_initial",
            "results_lessons_learned",
            "results_low_enrollment",
            "results_measure_impact",
            "results_no_usable_data",
            "results_recipe_errors",
            "results_restarts",
            "results_url",
            "review_advisory",
            "review_bugzilla",
            "review_comms",
            "review_data_steward",
            "review_engineering",
            "review_impacted_teams",
            "review_intent_to_ship",
            "review_legal",
            "review_qa_requested",
            "review_qa",
            "review_relman",
            "review_science",
            "review_security",
            "review_ux",
            "review_vp",
            "risk_brand",
            "risk_confidential",
            "risk_data_category",
            "risk_external_team_impact",
            "risk_fast_shipped",
            "risk_partner_related",
            "risk_release_population",
            "risk_revenue",
            "risk_revision",
            "risk_security",
            "risk_technical_description",
            "risk_technical",
            "risk_telemetry_data",
            "risk_ux",
            "risks",
            "rollout_playbook",
            "rollout_type",
            "short_description",
            "survey_instructions",
            "survey_required",
            "survey_urls",
            "test_builds",
            "testing",
            "total_enrolled_clients",
            "type",
            "variants",
            "windows_versions",
        )


def update_experiment_with_change_log(
    old_experiment, changed_data, user_email, message=None
):
    old_serialized_exp = ChangeLogSerializer(old_experiment).data
    ExperimentCore.objects.filter(id=old_experiment.id).update(**changed_data)
    new_experiment = ExperimentCore.objects.get(slug=old_experiment.slug)
    new_serialized_exp = ChangeLogSerializer(new_experiment).data

    default_user, _ = get_user_model().objects.get_or_create(
        email=user_email, username=user_email
    )

    generate_change_log(
        old_serialized_exp,
        new_serialized_exp,
        new_experiment,
        changed_data,
        default_user,
        message,
    )


def generate_change_log(
    old_serialized_vals,
    new_serialized_vals,
    instance,
    changed_data,
    user,
    message=None,
    form_fields=None,
):

    changed_values = {}
    old_status = None

    latest_change = instance.changes.latest()

    # account for changes in variant values
    if latest_change:
        old_status = latest_change.new_status
        if old_serialized_vals["variants"] != new_serialized_vals["variants"]:
            old_value = old_serialized_vals["variants"]
            new_value = new_serialized_vals["variants"]
            display_name = "Branches"
            changed_values["variants"] = {
                "old_value": old_value,
                "new_value": new_value,
                "display_name": display_name,
            }

    elif new_serialized_vals.get("variants"):
        old_value = None
        new_value = new_serialized_vals["variants"]
        display_name = "Branches"
        changed_values["variants"] = {
            "old_value": old_value,
            "new_value": new_value,
            "display_name": display_name,
        }

    if changed_data:
        if latest_change:
            old_status = latest_change.new_status

            for field in changed_data:
                old_val = None
                new_val = None

                if field in old_serialized_vals:
                    if field in ("countries", "locales"):
                        old_field_values = old_serialized_vals[field]
                        codes = [obj["code"] for obj in old_field_values]
                        old_val = codes
                    else:
                        old_val = old_serialized_vals[field]
                if field in new_serialized_vals:
                    if field in ("countries", "locales"):
                        new_field_values = new_serialized_vals[field]
                        codes = [obj["code"] for obj in new_field_values]
                        new_val = codes
                    else:
                        new_val = new_serialized_vals[field]

                display_name = _get_display_name(field, form_fields)

                if new_val != old_val:
                    changed_values[field] = {
                        "old_value": old_val,
                        "new_value": new_val,
                        "display_name": display_name,
                    }

        else:
            for field in changed_data:
                old_val = None
                new_val = None
                if field in new_serialized_vals:
                    if field in ("countries", "locales"):
                        new_field_values = new_serialized_vals[field]
                        codes = [obj["code"] for obj in new_field_values]
                        new_val = codes
                    else:
                        new_val = new_serialized_vals[field]
                    display_name = _get_display_name(field, form_fields)
                    changed_values[field] = {
                        "old_value": old_val,
                        "new_value": new_val,
                        "display_name": display_name,
                    }
    if _has_changed(old_status, changed_values, instance, message):
        ExperimentChangeLog.objects.create(
            experiment=instance,
            changed_by=user,
            old_status=old_status,
            new_status=instance.status,
            changed_values=changed_values,
            message=message,
        )


def _has_changed(old_status, changed_values, experiment, message):
    return changed_values or message or old_status != experiment.status


def _get_display_name(field, form_fields):
    if form_fields and form_fields[field].label:
        return form_fields[field].label
    return field.replace("_", " ").title()
