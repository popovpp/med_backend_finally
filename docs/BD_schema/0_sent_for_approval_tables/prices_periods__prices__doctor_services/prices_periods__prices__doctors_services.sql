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



CREATE TABLE "public.doctors_services" (
	"id" serial NOT NULL,
	"client_doctor_service_id" integer,
	"doctor_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	"is_active" bool NOT NULL,
	CONSTRAINT "doctors_services_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices_periods" (
	"id" serial NOT NULL,
	"start_date" DATE NOT NULL,
	"end_date" DATE NOT NULL,
	CONSTRAINT "prices_periods_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices" (
	"id" serial NOT NULL,
	"client_price_id" integer,
	"service_id" integer NOT NULL,
	"price_period_id" integer NOT NULL,
	"medical_center_id" integer NOT NULL,
	"private_price" float4 NOT NULL,
	"insuranced_price" float4 NOT NULL,
	CONSTRAINT "prices_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "services" ADD CONSTRAINT "services_fk0" FOREIGN KEY ("service_type_id") REFERENCES "sevices_types"("id");

ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_centers"("id");

ALTER TABLE "doctors_services" ADD CONSTRAINT "doctors_services_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");
ALTER TABLE "doctors_services" ADD CONSTRAINT "doctors_services_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");


ALTER TABLE "prices" ADD CONSTRAINT "prices_fk0" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk1" FOREIGN KEY ("price_period_id") REFERENCES "prices_periods"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk2" FOREIGN KEY ("medical_center_id") REFERENCES "medical_centers"("id");






