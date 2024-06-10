CREATE TABLE "public.users" (
	"id" serial NOT NULL,
	"client_user_id" integer UNIQUE DEFAULT 'null',
	"client_card_id" integer UNIQUE DEFAULT 'null',
	"client_personal_area_id" integer UNIQUE DEFAULT 'null',
	"first_name" varchar(100) NOT NULL,
	"last_name" varchar(100) NOT NULL,
	"patronymic" varchar(100) DEFAULT 'null',
	"birth_date" DATE NOT NULL,
	"gender" varchar(1) DEFAULT 'null',
	"email" varchar(100) NOT NULL UNIQUE,
	"phone_number" varchar(20) NOT NULL UNIQUE,
	"additional_phone_number" varchar(20) DEFAULT 'null',
	"password" varchar(50) DEFAULT 'null',
	"is_active" bool NOT NULL DEFAULT 'true',
	"is_verified" bool NOT NULL DEFAULT 'false',
	"created" DATE NOT NULL,
	"last_login" DATE,
	"last_visit" DATE,
	CONSTRAINT "users_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.user_relatives" (
	"id" serial NOT NULL,
	"user_id" integer NOT NULL,
	"user_relative_id" integer NOT NULL,
	"relationship_degree_id" integer NOT NULL,
	"is_legal_agend" bool NOT NULL,
	CONSTRAINT "user_relatives_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.relationship_degrees" (
	"id" serial NOT NULL,
	"client_relationship_degrees_id" integer,
	"name" varchar(10) NOT NULL,
	CONSTRAINT "relationship_degrees_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);




ALTER TABLE "user_relatives" ADD CONSTRAINT "user_relatives_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "user_relatives" ADD CONSTRAINT "user_relatives_fk1" FOREIGN KEY ("user_relative_id") REFERENCES "users"("id");
ALTER TABLE "user_relatives" ADD CONSTRAINT "user_relatives_fk2" FOREIGN KEY ("relationship_degree_id") REFERENCES "relationship_degrees"("id");





