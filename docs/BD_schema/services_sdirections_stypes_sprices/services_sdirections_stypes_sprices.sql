CREATE TABLE "public.services_directions" (
	"id" serial NOT NULL,
	"client_sdirection_id" integer,
	"name" varchar(100) NOT NULL UNIQUE,
	"description" TEXT,
	CONSTRAINT "services_directions_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.sevices_types" (
	"id" serial NOT NULL,
	"client_stype_id" integer,
	"name" varchar(100) NOT NULL UNIQUE,
	"description" integer,
	CONSTRAINT "sevices_types_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.services" (
	"id" serial NOT NULL,
	"client_service_id" integer,
	"service_direction_id" integer NOT NULL,
	"service_type_id" integer NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" TEXT NOT NULL,
	CONSTRAINT "services_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices" (
	"id" serial NOT NULL,
	"client_price_id" integer,
	"service_id" integer NOT NULL,
	"medical_center_id" integer NOT NULL,
	"medical_department_id" integer NOT NULL,
	"price" FLOAT NOT NULL,
	CONSTRAINT "prices_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



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
	CONSTRAINT "medical_center_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.medical_departments" (
	"id" serial NOT NULL,
	"client_department_id" integer,
	"name" varchar(200) NOT NULL UNIQUE,
	"description" TEXT,
	CONSTRAINT "medical_departments_pk" PRIMARY KEY ("id")
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
	CONSTRAINT "doctors_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.doctors_services" (
	"id" serial NOT NULL,
	"doctor_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	CONSTRAINT "doctors_services_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.medical_specialities" (
	"id" serial NOT NULL,
	"client_doctor_speciality_id" integer,
	"name" varchar(200) NOT NULL,
	"description" TEXT,
	CONSTRAINT "medical_specialities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);





ALTER TABLE "services" ADD CONSTRAINT "services_fk0" FOREIGN KEY ("service_direction_id") REFERENCES "services_directions"("id");
ALTER TABLE "services" ADD CONSTRAINT "services_fk1" FOREIGN KEY ("service_type_id") REFERENCES "sevices_types"("id");

ALTER TABLE "prices" ADD CONSTRAINT "prices_fk0" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk1" FOREIGN KEY ("medical_center_id") REFERENCES "medical_center"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk2" FOREIGN KEY ("medical_department_id") REFERENCES "medical_departments"("id");

ALTER TABLE "medical_center" ADD CONSTRAINT "medical_center_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");


ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_center"("id");
ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk1" FOREIGN KEY ("medical_department_id") REFERENCES "medical_departments"("id");
ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk2" FOREIGN KEY ("doctor_mspeciality_id") REFERENCES "medical_specialities"("id");

ALTER TABLE "doctors_services" ADD CONSTRAINT "doctors_services_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");
ALTER TABLE "doctors_services" ADD CONSTRAINT "doctors_services_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");











