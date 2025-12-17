/*  .\mongo-init\create_users_db.js */

"use strict"; 

// Placeholders pour les variables d'environnement
const targetDB = "__DB_NAME__"; 

db = db.getSiblingDB(targetDB);

// Fonction générique pour créer un utilisateur avec gestion d'erreurs
function createUserSafe(userParams) {
    try {
        db.createUser(userParams);
        print(`>> Utilisateur créé : ${userParams.user}`);
    } catch (e) {
        if (e.code === 51003) {
            print(`>> Utilisateur déjà existant (Ignoré) : ${userParams.user}`);
        } else {
            print(`>> ERREUR critique lors de la création de l'utilisateur ${userParams.user} : ${e.message}`);
            // On peut choisir d'arrêter le script ici ou de continuer. Ici, on continue.
        }
    }
}

// Utilisateur d'Administration de la Base de Données (dbOwner)
createUserSafe({
  user: "__OWNER_USER__",
  pwd: "__OWNER_PWD__",
  roles: [{ role: "dbOwner", db: targetDB }],
  comment: "Administrateur de la base de données, pour la gestion du schéma et des utilisateurs."
});

// Utilisateur Applicatif (readWrite)
createUserSafe({
  user: "__WRITER_USER__",
  pwd: "__WRITER_PWD__",
  roles: [{ role: "readWrite", db: targetDB }],
  comment: "Utilisateur applicatif principal, pour les opérations CRUD sur les données."
});

// Utilisateur d'Analyse (read)
createUserSafe({
  user: "__READER_USER__",
  pwd: "__READER_PWD__",
  roles: [{ role: "read", db: targetDB }],
  comment: "Utilisateur pour les outils de BI ou l'analyse en lecture seule."
});

print(`Création des utilisateurs terminée sur la base de données : ${targetDB}`);