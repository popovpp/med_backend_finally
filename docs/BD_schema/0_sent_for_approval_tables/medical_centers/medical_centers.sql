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



ALTER TABLE "medical_centers" ADD CONSTRAINT "medical_centers_fk0" FOREIGN KEY ("city_id") REFERENCES "cities"("id");


