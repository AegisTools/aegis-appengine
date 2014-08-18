Data Models
===========

User
----

Describes a particular user in the system.

* user (User)
* created_by (Key: User)
* creaded (DateTime)
* updated (DateTime)
* active (Boolean)
* notes (Text)

Permission
----------

Describes a single permission granted to a user, possibly for a specific item.

**TODO:** Should user by a (Key: User)?  Should we add created_by?  Should id be a (Key: *)?
Should parent be (Key: User)?

* user (User)
* type (String)
* id (String, optional)
* action (String)
* created (DateTime)

Tag
---

Describes a particular tag.

* parent (Key: Tag, None)
* created_by (Key: User)
* created (DateTime)

AppliedTag
----------

Indicates that a tag has actually been applied to an object.

* parent (Key: Tag)
* applied_by (Key: User)
* applied (DateTime)
* target (Key: *)


