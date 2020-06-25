# Generated by Django 3.0.7 on 2020-06-25 22:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0101_auto_20200623_2355"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExperimentBucketNamespace",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("instance", models.PositiveIntegerField(default=1)),
                ("total", models.PositiveIntegerField(default=10000)),
                (
                    "randomization_unit",
                    models.CharField(default="normandy_id", max_length=255),
                ),
            ],
            options={
                "verbose_name": "Experiment Bucket Namespace",
                "verbose_name_plural": "Experiment Bucket Namespaces",
                "ordering": ("name", "instance"),
                "unique_together": {("name", "instance")},
            },
        ),
        migrations.CreateModel(
            name="ExperimentBucket",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.PositiveIntegerField()),
                ("count", models.PositiveIntegerField()),
                (
                    "experiment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bucket",
                        to="experiments.Experiment",
                    ),
                ),
                (
                    "namespace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buckets",
                        to="experiments.ExperimentBucketNamespace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Experiment Bucket",
                "verbose_name_plural": "Experiment Buckets",
            },
        ),
    ]
