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



CREATE TABLE "public.access_tickets" (
	"id" serial NOT NULL,
	"client_access_ticket_id" integer,
	"ticket_time" DATE,
	"ticket_duration" integer NOT NULL DEFAULT '15',
	"doctor_id" integer,
	"ticket_was_used" bool NOT NULL,
	"description" TEXT,
	"is_active" bool NOT NULL,
	CONSTRAINT "access_tickets_pk" PRIMARY KEY ("id")
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



CREATE TABLE "public.users_services_schedules" (
	"id" serial NOT NULL,
	"client_user_services_schedule_id" integer,
	"access_ticket_id" integer,
	"service_time" DATE,
	"user_id" integer NOT NULL,
	"medical_center_id" integer,
	"sevices_id" integer,
	"price_id" integer,
	"user_subscription_id" integer,
	"user_payment_id" integer,
	"doctor_who_prescribed" integer,
	"doctor_who_performed" integer,
	"user_service_type_id" integer NOT NULL,
	"service_was_used" bool NOT NULL DEFAULT 'false',
	"is_active" bool NOT NULL DEFAULT 'true',
	CONSTRAINT "users_services_schedules_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices" (
	"id" serial NOT NULL,
	"client_price_id" integer,
	"price_name_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	"price_period_id" integer NOT NULL,
	"price_type_id" integer NOT NULL,
	"price" float4 NOT NULL,
	CONSTRAINT "prices_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices_types" (
	"id" serial NOT NULL,
	"client_price_type_id" integer,
	"name" varchar(100) NOT NULL UNIQUE,
	"description" varchar(500),
	"is_active" bool NOT NULL,
	CONSTRAINT "prices_types_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_payments" (
	"id" serial NOT NULL,
	"client_user_payment_id" integer,
	"payment_system_id" integer NOT NULL,
	"payment_date" TIME NOT NULL,
	"user_id" integer NOT NULL,
	"amount_to_pay" float4 NOT NULL,
	"paid_amount" float4 NOT NULL DEFAULT '0',
	"payment_status" integer NOT NULL,
	"payment_transaction_id" integer NOT NULL,
	CONSTRAINT "users_payments_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_services_types" (
	"id" serial NOT NULL,
	"client_service_type_id" integer,
	"name" varchar NOT NULL UNIQUE,
	"describtion" varchar,
	"is_active" bool NOT NULL DEFAULT 'true',
	CONSTRAINT "users_services_types_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices_names" (
	"id" serial NOT NULL,
	"client_price_name_id" integer,
	"name" varchar(200) NOT NULL UNIQUE,
	"description" varchar(500),
	"is_active" bool(true) NOT NULL,
	CONSTRAINT "prices_names_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "services" ADD CONSTRAINT "services_fk0" FOREIGN KEY ("service_type_id") REFERENCES "services_types"("id");

ALTER TABLE "access_tickets" ADD CONSTRAINT "access_tickets_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");

ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_centers"("id");

ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk0" FOREIGN KEY ("access_ticket_id") REFERENCES "access_tickets"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk1" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk2" FOREIGN KEY ("medical_center_id") REFERENCES "undefined"("undefined");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk3" FOREIGN KEY ("sevices_id") REFERENCES "services"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk4" FOREIGN KEY ("price_id") REFERENCES "prices"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk5" FOREIGN KEY ("user_subscription_id") REFERENCES "users_subscriptions"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk6" FOREIGN KEY ("user_payment_id") REFERENCES "users_payments"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk7" FOREIGN KEY ("doctor_who_prescribed") REFERENCES "doctors"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk8" FOREIGN KEY ("doctor_who_performed") REFERENCES "doctors"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk9" FOREIGN KEY ("user_service_type_id") REFERENCES "users_services_types"("id");

ALTER TABLE "prices" ADD CONSTRAINT "prices_fk0" FOREIGN KEY ("price_name_id") REFERENCES "prices_names"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk2" FOREIGN KEY ("price_period_id") REFERENCES "prices_periods"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk3" FOREIGN KEY ("price_type_id") REFERENCES "prices_types"("id");


ALTER TABLE "users_payments" ADD CONSTRAINT "users_payments_fk0" FOREIGN KEY ("payment_system_id") REFERENCES "undefined"("undefined");
ALTER TABLE "users_payments" ADD CONSTRAINT "users_payments_fk1" FOREIGN KEY ("user_id") REFERENCES "users"("id");












