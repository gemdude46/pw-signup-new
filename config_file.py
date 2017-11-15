
capacity = 4

admin_password = '$2b$12$Rz9Z4HWX4cU4COBr9dUIv.IcA3VpNAeUqvCJY9063apFrVwjVhI9m'

database_URI = 'sqlite:///db.db'

fields = [
	dict(dispname="Full Name:", intname="name", type="text", required=True),
	dict(dispname="Email Address:", intname="email", type="email", required=True),
	dict(dispname="Mobile Phone Number:", intname="mobile", type="text", length=16),
	dict(dispname="Any allergies or specific dietary requirements?", intname="allergies", type="text", length=256),
	dict(dispname="Any medication it would be useful for us to know about?", intname="medication", type="text", length=256),
	dict(dispname="Any illnesses, injuries or conditions that it would be useful for us to know about?", intname="conditions", type="text", length=256),
	dict(dispname="A website, blog, etc?", intname="website", type="text"),
	dict(dispname="Partial date of birth (Month/Year):", intname="dob", type="text", pad=True, length=16),
	dict(dispname="Any disabilities?", intname="disabilities", type="text"),
	dict(dispname="Place of Residence Postcode:", intname="postcode", type="text", length=16),
	dict(dispname="Gender:", intname="gender", type="text"),
	dict(dispname="Ethnicity:", intname="ethnicity", type="text"),
	dict(dispname="Religion:", intname="religion", type="text"),
	dict(dispname="Emergency Contact 1:", intname="ignore_ec1", type="hidden", pad=True),
	dict(dispname="Name:", intname="emergency_contact_1_name", type="text", required=True, indent=True),
	dict(dispname="Relation to Member:", intname="emergency_contact_1_relation", type="text", required=True, indent=True),
	dict(dispname="Phone Number:", intname="emergency_contact_1_phone", type="text", required=True, indent=True, length=16),
	dict(dispname="Email:", intname="emergency_contact_1_email", type="email", required=True, indent=True),
	dict(dispname="Emergency Contact 2:", intname="ignore_ec2", type="hidden", pad=True),
	dict(dispname="Name:", intname="emergency_contact_2_name", type="text", required=True, indent=True),
	dict(dispname="Relation to Member:", intname="emergency_contact_2_relation", type="text", required=True, indent=True),
	dict(dispname="Phone Number:", intname="emergency_contact_2_phone", type="text", required=True, indent=True, length=16),
	dict(dispname="Email:", intname="emergency_contact_2_email", type="email", required=True, indent=True)
]

ico = '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'.decode('base64').decode('zip')

secret_key = 'SuperDuperSecret'
