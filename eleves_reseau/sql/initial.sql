drop database if exists la_salle;
create database la_salle;
use la_salle;
create table grades (
id tinyint not null primary key,
name varchar(50) not null
);
insert into grades 
values (12, "terminal"), (11, "premiere"), (10, "deuxieme"), (9, "troisieme");
create table users (
username varchar(50) primary key not null,
password varchar(50) not null,
name varchar(50) not null,
grade_id tinyint not null,
internship varchar(50),
profile_photo mediumtext,
bio varchar(255),
foreign key (grade_id) references grades(id)
);
create table calendars (
username varchar(50) primary key,
mon TIME not null,
tue TIME not null,
wed TIME not null,
thu TIME not null,
fri TIME not null,
foreign key (username) references users(username) on delete cascade
);
create table groups_t (
id int not null auto_increment primary key,
initial_grade tinyint not null,
foreign key (initial_grade) references grades(id)
);
create table grouping_t (
username varchar(50) not null primary key,
group_id int not null,
foreign key(username) references users(username) on delete cascade,
foreign key (group_id) references groups_t(id)
);
create table relationship_types (
id tinyint not null auto_increment primary key,
name varchar(50) not null
);
insert into relationship_types (name)
values ('abonné(s)'), ('bloqué(s)');
create table relationships (
f_username varchar(50) not null,
t_username varchar(50) not null,
relationship_id tinyint not null,
primary key (f_username, t_username),
foreign key (relationship_id) references relationship_types(id),
foreign key (f_username) references users(username) on delete cascade,
foreign key (t_username) references users(username) on delete cascade
);
create table searches (
f_username varchar(50) not null,
t_username varchar(50) not null,
date timestamp not null default current_timestamp,
foreign key (f_username) references users(username) on delete cascade,
foreign key (t_username) references users(username) on delete cascade,
primary key (f_username, t_username)
);
create table grouping_history 
(username varchar(50) not null, 
f_group_id int not null, 
t_group_id int not null, 
date timestamp default current_timestamp);