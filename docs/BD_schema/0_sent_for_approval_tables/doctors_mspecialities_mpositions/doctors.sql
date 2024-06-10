CREATE TABLE "public.doctors" (
	"id" serial NOT NULL,
	"client_doctor_id" integer UNIQUE,
	"medical_center_id" integer NOT NULL,
	"fio" varchar(300) NOT NULL,
	"description" TEXT,
	"photo" varchar(100),
	"is_active" bool NOT NULL,
	"phone_number" varchar(25),
	"mobile_number" varchar(25),
	"email" varchar(100),
	CONSTRAINT "doctors_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.medical_positions" (
	"id" serial NOT NULL,
	"client_doctor_position_id" integer,
	"view_name" varchar(200) NOT NULL,
	"searching_name" integer NOT NULL,
	"view_description" TEXT,
	"searching_description" integer NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "medical_positions_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.doctors_mpositions" (
	"id" serial NOT NULL,
	"doctor_id" integer NOT NULL,
	"medical_position_id" integer NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "doctors_mpositions_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.medical_specialities" (
	"id" serial NOT NULL,
	"client_doctor_speciality_id" integer,
	"view_name" varchar(200) NOT NULL,
	"searching_name" varchar(200),
	"view_description" TEXT,
	"searching_description" TEXT,
	"is_active" bool NOT NULL,
	CONSTRAINT "medical_specialities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.doctors_mspecialities" (
	"id" serial NOT NULL,
	"doctor_id" integer NOT NULL,
	"medical_speciality_id" integer NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "doctors_mspecialities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_centers"("id");


ALTER TABLE "doctors_mpositions" ADD CONSTRAINT "doctors_mpositions_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");
ALTER TABLE "doctors_mpositions" ADD CONSTRAINT "doctors_mpositions_fk1" FOREIGN KEY ("medical_position_id") REFERENCES "medical_positions"("id");


ALTER TABLE "doctors_mspecialities" ADD CONSTRAINT "doctors_mspecialities_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");
ALTER TABLE "doctors_mspecialities" ADD CONSTRAINT "doctors_mspecialities_fk1" FOREIGN KEY ("medical_speciality_id") REFERENCES "medical_specialities"("id");






