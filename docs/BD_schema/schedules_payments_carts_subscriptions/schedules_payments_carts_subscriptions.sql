CREATE TABLE "public.doctors" (
	"id" serial NOT NULL,
	"client_doctor_id" integer UNIQUE,
	"medical_center_id" integer NOT NULL,
	"medical_department_id" integer NOT NULL,
	"doctor_mspeciality_id" integer NOT NULL,
	"fio" varchar(300) NOT NULL,
	"description" TEXT,
	"photo" varchar(100),
	"is_active" BOOLEAN NOT NULL,
	CONSTRAINT "doctors_pk" PRIMARY KEY ("id")
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
	"is_active" BOOLEAN NOT NULL,
	CONSTRAINT "medical_center_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.cities" (
	"id" serial NOT NULL,
	"client_city_id" integer UNIQUE,
	"name" varchar(20) NOT NULL,
	"is_active" BOOLEAN NOT NULL,
	CONSTRAINT "cities_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.doctors_schedules" (
	"id" serial NOT NULL,
	"doctor_id" integer NOT NULL,
	"plan_visit_datetime" TIME NOT NULL,
	"plan_visit_duration" integer NOT NULL,
	"description" TEXT NOT NULL,
	"is_available" BOOLEAN NOT NULL,
	CONSTRAINT "doctors_schedules_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.user_schedules" (
	"id" serial NOT NULL,
	"client_rnumb_id" integer,
	"plan_visit_time" TIME NOT NULL,
	"paln_visit_duration" integer NOT NULL,
	"user_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	"doctor_id" integer NOT NULL,
	"payment_id" integer,
	"subscription_id" integer,
	"user_comments" TEXT,
	"visit_was_done" BOOLEAN NOT NULL DEFAULT 'false',
	"is_active" integer NOT NULL DEFAULT 'true',
	CONSTRAINT "user_schedules_pk" PRIMARY KEY ("id")
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
	"is_active" BOOLEAN NOT NULL,
	CONSTRAINT "services_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_carts" (
	"id" serial NOT NULL,
	"user_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	"doctor_id" integer,
	"price" FLOAT NOT NULL,
	"discount" FLOAT,
	"amount_to_pay" FLOAT NOT NULL,
	"needed_datetime" TIME,
	CONSTRAINT "users_carts_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



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



CREATE TABLE "public.users_payments" (
	"id" serial NOT NULL,
	"payment_date" TIME NOT NULL,
	"user_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	"doctor_id" integer NOT NULL,
	"price" FLOAT NOT NULL,
	"discount" integer NOT NULL,
	"amount_to_pay" FLOAT NOT NULL,
	"payment_amount" FLOAT NOT NULL,
	"payment_status" integer NOT NULL,
	"payment_transaction_id" integer NOT NULL,
	CONSTRAINT "users_payments_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.users_subscribtions_items" (
	"id" serial NOT NULL,
	"user_subscription_id" integer NOT NULL,
	"service_id" integer NOT NULL,
	"price" FLOAT NOT NULL,
	"discount" integer NOT NULL,
	"amount" FLOAT NOT NULL,
	"is_paid" BOOLEAN DEFAULT 'false',
	"is_got" BOOLEAN DEFAULT 'false',
	"is_active" BOOLEAN NOT NULL DEFAULT 'false',
	CONSTRAINT "users_subscribtions_items_pk" PRIMARY KEY ("id")
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



ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk0" FOREIGN KEY ("medical_center_id") REFERENCES "medical_center"("id");
ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk1" FOREIGN KEY ("medical_department_id") REFERENCES "medical_departments"("id");
ALTER TABLE "doctors" ADD CONSTRAINT "doctors_fk2" FOREIGN KEY ("doctor_mspeciality_id") REFERENCES "medical_specialities"("id");

ALTER TABLE "medical_center" ADD CONSTRAINT "medical_center_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");


ALTER TABLE "doctors_schedules" ADD CONSTRAINT "doctors_schedules_fk0" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");

ALTER TABLE "user_schedules" ADD CONSTRAINT "user_schedules_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "user_schedules" ADD CONSTRAINT "user_schedules_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "user_schedules" ADD CONSTRAINT "user_schedules_fk2" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");
ALTER TABLE "user_schedules" ADD CONSTRAINT "user_schedules_fk3" FOREIGN KEY ("payment_id") REFERENCES ""("");

ALTER TABLE "services" ADD CONSTRAINT "services_fk0" FOREIGN KEY ("service_direction_id") REFERENCES "services_directions"("id");
ALTER TABLE "services" ADD CONSTRAINT "services_fk1" FOREIGN KEY ("service_type_id") REFERENCES "sevices_types"("id");

ALTER TABLE "users_carts" ADD CONSTRAINT "users_carts_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_carts" ADD CONSTRAINT "users_carts_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "users_carts" ADD CONSTRAINT "users_carts_fk2" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");


ALTER TABLE "users_payments" ADD CONSTRAINT "users_payments_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_payments" ADD CONSTRAINT "users_payments_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");
ALTER TABLE "users_payments" ADD CONSTRAINT "users_payments_fk2" FOREIGN KEY ("doctor_id") REFERENCES "doctors"("id");

ALTER TABLE "users_subscribtions_items" ADD CONSTRAINT "users_subscribtions_items_fk0" FOREIGN KEY ("user_subscription_id") REFERENCES "users_subscriptions"("id");
ALTER TABLE "users_subscribtions_items" ADD CONSTRAINT "users_subscribtions_items_fk1" FOREIGN KEY ("service_id") REFERENCES "services"("id");

ALTER TABLE "users_subscriptions" ADD CONSTRAINT "users_subscriptions_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");












