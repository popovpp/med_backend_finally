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
	"access_ticket_id" integer NOT NULL,
	"user_id" integer,
	"price_id" integer,
	"user_subscription_item_id" integer,
	"is_active" integer NOT NULL DEFAULT 'true',
	CONSTRAINT "users_services_schedules_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.prices" (
	"id" serial NOT NULL,
	"client_price_id" integer,
	"service_id" integer NOT NULL,
	"price_period_id" integer NOT NULL,
	"medical_center_id" integer NOT NULL,
	"service_place_type_id" integer NOT NULL,
	"private_price" float4 NOT NULL,
	"insuranced_price" float4 NOT NULL,
	CONSTRAINT "prices_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_subscriptions" (
	"id" serial NOT NULL,
	"client_usubscription_id" integer NOT NULL,
	"user_id" integer NOT NULL,
	"description" TEXT,
	"is_paid" BOOLEAN NOT NULL DEFAULT 'false',
	"price" FLOAT NOT NULL DEFAULT '0',
	"common_discount" integer,
	"amount" FLOAT NOT NULL,
	"paid_amount" FLOAT NOT NULL DEFAULT '0',
	"current_amount" FLOAT NOT NULL DEFAULT '0',
	"is_active" BOOLEAN NOT NULL DEFAULT 'false',
	CONSTRAINT "users_subscriptions_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_subscribtions_items" (
	"id" serial NOT NULL,
	"user_subscription_id" integer NOT NULL,
	"price_id" integer NOT NULL,
	"discount" integer NOT NULL,
	"amount" FLOAT NOT NULL,
	"is_paid" BOOLEAN DEFAULT 'false',
	"is_got" BOOLEAN DEFAULT 'false',
	"is_active" BOOLEAN NOT NULL DEFAULT 'false',
	CONSTRAINT "users_subscribtions_items_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "services" ADD CONSTRAINT "services_fk0" FOREIGN KEY ("service_type_id") REFERENCES "services_types"("id");

ALTER TABLE "access_tickets" ADD CONSTRAINT "access_tickets_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");

ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_centers"("id");

ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk0" FOREIGN KEY ("access_ticket_id") REFERENCES "access_tickets"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk1" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk2" FOREIGN KEY ("price_id") REFERENCES "prices"("id");
ALTER TABLE "users_services_schedules" ADD CONSTRAINT "users_services_schedules_fk3" FOREIGN KEY ("user_subscription_item_id") REFERENCES "users_subscribtions_items"("id");

ALTER TABLE "prices" ADD CONSTRAINT "prices_fk0" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk1" FOREIGN KEY ("price_period_id") REFERENCES "prices_periods"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk2" FOREIGN KEY ("medical_center_id") REFERENCES "medical_centers"("id");
ALTER TABLE "prices" ADD CONSTRAINT "prices_fk3" FOREIGN KEY ("service_place_type_id") REFERENCES "sevices_places_types"("id");

ALTER TABLE "users_subscriptions" ADD CONSTRAINT "users_subscriptions_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");

ALTER TABLE "users_subscribtions_items" ADD CONSTRAINT "users_subscribtions_items_fk0" FOREIGN KEY ("user_subscription_id") REFERENCES "users_subscriptions"("id");
ALTER TABLE "users_subscribtions_items" ADD CONSTRAINT "users_subscribtions_items_fk1" FOREIGN KEY ("price_id") REFERENCES "prices"("id");








