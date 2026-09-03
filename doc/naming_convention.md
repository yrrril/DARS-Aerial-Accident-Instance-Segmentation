DARS Naming Convention

This document describes the naming convention used to organize DARS images and annotations.

1. General Rule

Each image and its corresponding annotation file use the same base name.

Example:

event0001_001.jpg
event0001_001.json

The default naming pattern is:

<event_id>_<sample_id>

where:

<event_id> identifies an accident event or scene group;

<sample_id> identifies an individual image within that event.

The default separator is an underscore (_).

2. Event Identifier

Images originating from the same accident event share the same <event_id>.

For example:

event0001_001.jpg
event0001_002.jpg
event0001_003.jpg

These images belong to the same event group and must remain in the same dataset subset during event-level splitting.

The public splitting script extracts the event identifier from the file name by removing the final separator and sample identifier. A different separator can be specified through the command-line argument of event_level_split.py.

3. Image–Annotation Correspondence

Each image and its LabelMe annotation file must have identical base names.

Example:

event0123_004.jpg
event0123_004.json

This one-to-one naming rule is used by the annotation-conversion and dataset-splitting scripts.

4. Supported Image Extensions

The public scripts support commonly used image extensions, including:

.jpg
.jpeg
.png

Upper-case variants are also supported where applicable.

5. Privacy and Source Information

File names used for DARS processing do not encode personal information, platform account names, or other source-identifying information.

The naming convention is intended only to support consistent image–annotation matching and event-level dataset organization.
