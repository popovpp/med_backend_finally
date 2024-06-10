CREATE TABLE "public.medical_center" (
	"id" serial NOT NULL,
	"client_mcenter_id" integer,
	"city_id" integer NOT NULL,
	"name" varchar(200) NOT NULL,
	"address" TEXT(200) NOT NULL,
	"longitude" float8,
	"latitude" float8,
	"description" TEXT,
	"inn" varchar(20) NOT NULL,
	"bank_bic" varchar(20) NOT NULL,
	"settlement_account" varchar(40) NOT NULL,
	"correspondent_account" varchar(40) NOT NULL,
	"kpp" varchar(40) NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "medical_center_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.doctors" (
	"id" serial NOT NULL,
	"client_doctor_id" integer UNIQUE,
	"medical_center_id" integer NOT NULL,
	"medical_department_id" integer NOT NULL,
	"doctor_mspeciality_id" integer NOT NULL,
	"fio" varchar(300) NOT NULL,
	"description" TEXT,
	"photo" varchar(100),
	"is_active" bool NOT NULL,
	CONSTRAINT "doctors_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.cities" (
	"id" serial NOT NULL,
	"client_city_id" integer UNIQUE,
	"name" varchar(20) NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "cities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.medical_departments" (
	"id" serial NOT NULL,
	"client_department_id" integer,
	"name" varchar(200) NOT NULL UNIQUE,
	"description" TEXT,
	"is_active" bool NOT NULL,
	CONSTRAINT "medical_departments_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.mcenters_mdepartments" (
	"id" serial NOT NULL,
	"medical_center_id" integer NOT NULL,
	"medical_department_id" integer NOT NULL,
	"description" TEXT,
	"is_active" bool NOT NULL,
	CONSTRAINT "mcenters_mdepartments_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.medical_specialities" (
	"id" serial NOT NULL,
	"client_doctor_speciality_id" integer,
	"name" varchar(200) NOT NULL,
	"description" TEXT,
	"is_active" bool NOT NULL,
	CONSTRAINT "medical_specialities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "medical_center" ADD CONSTRAINT "medical_center_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");

ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_center"("id");
ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk1" FOREIGN KEY ("medical_department_id") REFERENCES "medical_departments"("id");
ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk2" FOREIGN KEY ("doctor_mspeciality_id") REFERENCES "medical_specialities"("id");



ALTER TABLE "mcenters_mdepartments" ADD CONSTRAINT "mcenters_mdepartments_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_center"("id");
ALTER TABLE "mcenters_mdepartments" ADD CONSTRAINT "mcenters_mdepartments_fk1" FOREIGN KEY ("medical_department_id") REFERENCES "medical_departments"("id");








