CREATE TABLE "public.services" (
	"id" serial NOT NULL,
	"client_service_id" integer,
	"service_type_id" integer NOT NULL,
	"name" varchar(100) NOT NULL,
	"comment" varchar(500),
	"description" TEXT,
	"applied_method" varchar(500),
	"preparation_rules" TEXT,
	"is_active" bool,
	CONSTRAINT "services_pk" PRIMARY KEY ("id")
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



CREATE TABLE "public.services_mspeciaslities" (
	"id" serial NOT NULL,
	"service_id" integer NOT NULL,
	"medical_speciality_id" integer NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "services_mspeciaslities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.services_types" (
	"id" serial NOT NULL,
	"client_service_type_id" integer,
	"name" varchar(100) NOT NULL UNIQUE,
	"description" varchar(500),
	"is_active" bool NOT NULL,
	CONSTRAINT "services_types_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "services" ADD CONSTRAINT "services_fk0" FOREIGN KEY ("service_type_id") REFERENCES "services_types"("id");


ALTER TABLE "services_mspeciaslities" ADD CONSTRAINT "services_mspeciaslities_fk0" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "services_mspeciaslities" ADD CONSTRAINT "services_mspeciaslities_fk1" FOREIGN KEY ("medical_speciality_id") REFERENCES "medical_specialities"("id");






