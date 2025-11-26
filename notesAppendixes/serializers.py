from rest_framework import serializers

from notes.models import Note
from .models import NotesAppendixes


class NotesAppendixesSerializer(serializers.ModelSerializer):
    note_public_id = serializers.CharField(write_only=True)
    note = serializers.CharField(source="note_id.public_id", read_only=True)

    class Meta:
        model = NotesAppendixes
        fields = [
            "public_id",
            "note_public_id",
            "note",
            "MCQ",
            "summary",
        ]
        read_only_fields = ["public_id", "note"]

    def create(self, validated_data):
        note_public_id = validated_data.pop("note_public_id")
        note = self._get_note_by_public_id(note_public_id)
        if NotesAppendixes.objects.filter(note_id=note).exists():
            raise serializers.ValidationError(
                {"note_public_id": "Appendix already exists for this note."}
            )
        return NotesAppendixes.objects.create(note_id=note, **validated_data)

    def update(self, instance, validated_data):
        note_public_id = validated_data.pop("note_public_id", None)

        if note_public_id:
            note = self._get_note_by_public_id(note_public_id)
            if (
                NotesAppendixes.objects.filter(note_id=note)
                .exclude(pk=instance.pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    {"note_public_id": "Appendix already exists for this note."}
                )
            instance.note_id = note

        instance.MCQ = validated_data.get("MCQ", instance.MCQ)
        instance.summary = validated_data.get("summary", instance.summary)
        instance.save()

        return instance

    def _get_note_by_public_id(self, public_id: str) -> Note:
        try:
            return Note.objects.get(public_id=public_id)
        except Note.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"note_public_id": "Note with the provided public_id was not found."}
            ) from exc

