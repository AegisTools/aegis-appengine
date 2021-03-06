Data Models
===========

users/User
----------

Describes a particular user in the system.

* user (User)
* created_by (Key: User)
* creaded (DateTime)
* updated (DateTime)
* active (Boolean)
* notes (Text)

users/Permission
----------------

Describes a single permission granted to a user, possibly for a specific item.

* parent (Key: User, type, action, id.url_safe())
* type (String)
* target (Key: *)
* action (String)
* granted (DateTime)
* granted_by (Key: User)

tags/Tag
--------

Describes a particular tag.

* parent (Key: Tag, None)
* name (String)
* created_by (Key: User)
* created (DateTime)

tags/AppliedTag
---------------

Indicates that a tag has actually been applied to an object.

* parent (Key: Tag)
* applied_by (Key: User)
* applied (DateTime)
* target (Key: *)


