CREATE TABLE "public.users" (
	"id" serial NOT NULL,
	"client_card_id" integer UNIQUE DEFAULT 'null',
	"first_name" varchar(100) NOT NULL,
	"last_name" varchar(100) NOT NULL,
	"patronymic" varchar(100) DEFAULT 'null',
	"birth_date" DATE NOT NULL,
	"gender" varchar(1) DEFAULT 'null',
	"email" varchar(100) NOT NULL UNIQUE,
	"phone_number" varchar(20) NOT NULL UNIQUE,
	"additional_phone_number" varchar(20) DEFAULT 'null',
	"password" varchar(200) DEFAULT 'null',
	"is_active" bool NOT NULL DEFAULT 'true',
	"is_verified" bool NOT NULL DEFAULT 'false',
	"created" DATE NOT NULL,
	"last_login" DATE,
	"last_visit" DATE,
	"city_id" integer NOT NULL,
	"address" varchar(200) NOT NULL,
	"longitude" float4,
	"latitude" float4,
	"inn" varchar(20),
	"snils" varchar(20),
	"default_medical_center_id" integer,
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



CREATE TABLE "public.medical_centers" (
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
	"manager_position" varchar(100),
	"namager_fio" varchar(300),
	"legal_entity" varchar(500),
	"legal_address" varchar(1000),
	"registration_number" varchar(50),
	"registration_date" DATE,
	"license_number" varchar(50),
	"license_date" DATE,
	"vk_link" varchar(100),
	"ogrn" varchar(50),
	CONSTRAINT "medical_centers_pk" PRIMARY KEY ("id")
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



ALTER TABLE "users" ADD CONSTRAINT "users_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");
ALTER TABLE "users" ADD CONSTRAINT "users_fk1" FOREIGN KEY ("default_medical_center_id") REFERENCES "medical_centers"("id");

ALTER TABLE "user_relatives" ADD CONSTRAINT "user_relatives_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "user_relatives" ADD CONSTRAINT "user_relatives_fk1" FOREIGN KEY ("user_relative_id") REFERENCES "users"("id");
ALTER TABLE "user_relatives" ADD CONSTRAINT "user_relatives_fk2" FOREIGN KEY ("relationship_degree_id") REFERENCES "relationship_degrees"("id");


ALTER TABLE "medical_centers" ADD CONSTRAINT "medical_centers_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");







