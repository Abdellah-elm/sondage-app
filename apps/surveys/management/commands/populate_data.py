"""
Commande Django : populate_data
Remplit la base avec des données de test réalistes.
Usage : python manage.py populate_data
"""
import random
import hashlib
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from apps.accounts.models import Utilisateur, Profil
from apps.surveys.models import Sondage, SectionSondage, Question, Choix, LienPartage
from apps.responses.models import Soumission, Reponse, ReponseChoix
from apps.analytics.models import StatistiqueSondage
from apps.dashboard.models import Notification


PASSWORD = make_password('pass1234')

UTILISATEURS = [
    {'username': 'marie.dupont',  'prenom': 'Marie',   'nom': 'Dupont',   'email': 'marie@demo.com',    'role': 'createur'},
    {'username': 'ahmed.benali',  'prenom': 'Ahmed',   'nom': 'Benali',   'email': 'ahmed@demo.com',    'role': 'createur'},
    {'username': 'jean.martin',   'prenom': 'Jean',    'nom': 'Martin',   'email': 'jean@demo.com',     'role': 'visiteur'},
    {'username': 'sophie.l',      'prenom': 'Sophie',  'nom': 'Lefebvre', 'email': 'sophie@demo.com',   'role': 'visiteur'},
    {'username': 'youssef.k',     'prenom': 'Youssef', 'nom': 'Khalil',   'email': 'youssef@demo.com',  'role': 'visiteur'},
    {'username': 'leila.m',       'prenom': 'Leïla',   'nom': 'Mansouri', 'email': 'leila@demo.com',    'role': 'visiteur'},
]

# ─── Données des sondages ──────────────────────────────────────────────────────

SONDAGES_DATA = [
    {
        'titre': 'Satisfaction client 2024',
        'description': 'Aidez-nous à améliorer nos services en répondant à quelques questions rapides.',
        'theme': 'defaut',
        'createur': 'marie.dupont',
        'sections': [
            {
                'titre': 'Votre expérience globale',
                'questions': [
                    {
                        'texte': 'Comment évaluez-vous votre satisfaction globale ?',
                        'type': 'echelle', 'min': 1, 'max': 10,
                        'libelle_min': 'Très insatisfait', 'libelle_max': 'Très satisfait',
                    },
                    {
                        'texte': 'Recommanderiez-vous nos services à un ami ou collègue ?',
                        'type': 'choix_unique',
                        'choix': ['Oui, certainement', 'Probablement oui', 'Probablement non', 'Non, pas du tout'],
                    },
                    {
                        'texte': 'Quels aspects avez-vous le plus appréciés ?',
                        'type': 'choix_multiple',
                        'choix': ['Qualité du service', 'Rapidité', 'Prix', 'Accueil', 'Support client'],
                        'obligatoire': False,
                    },
                ],
            },
            {
                'titre': 'Commentaires',
                'questions': [
                    {
                        'texte': 'Avez-vous des suggestions pour améliorer nos services ?',
                        'type': 'texte', 'obligatoire': False,
                    },
                ],
            },
        ],
    },
    {
        'titre': 'Enquête bien-être au travail',
        'description': 'Sondage anonyme pour évaluer le bien-être de nos équipes.',
        'theme': 'moderne',
        'createur': 'marie.dupont',
        'est_anonyme': True,
        'sections': [
            {
                'titre': 'Environnement de travail',
                'questions': [
                    {
                        'texte': 'Comment évaluez-vous votre niveau de stress au travail ?',
                        'type': 'echelle', 'min': 1, 'max': 5,
                        'libelle_min': 'Pas du tout stressé', 'libelle_max': 'Très stressé',
                    },
                    {
                        'texte': 'Êtes-vous satisfait de l\'équilibre vie professionnelle / vie personnelle ?',
                        'type': 'choix_unique',
                        'choix': ['Très satisfait', 'Satisfait', 'Neutre', 'Insatisfait', 'Très insatisfait'],
                    },
                    {
                        'texte': 'Souhaitez-vous préciser vos difficultés ?',
                        'type': 'texte', 'obligatoire': False,
                        'conditionnel': True,  # sera lié après
                    },
                ],
            },
            {
                'titre': 'Relations d\'équipe',
                'questions': [
                    {
                        'texte': 'Comment décrivez-vous l\'ambiance dans votre équipe ?',
                        'type': 'choix_unique',
                        'choix': ['Excellente', 'Bonne', 'Correcte', 'Tendue', 'Très difficile'],
                    },
                    {
                        'texte': 'Vos suggestions pour améliorer l\'esprit d\'équipe',
                        'type': 'texte', 'obligatoire': False,
                    },
                ],
            },
        ],
    },
    {
        'titre': 'Évaluation formation Django',
        'description': 'Donnez votre avis sur la formation Django MVT que vous venez de suivre.',
        'theme': 'professionnel',
        'createur': 'ahmed.benali',
        'duree_limite_minutes': 15,
        'sections': [
            {
                'titre': 'Contenu pédagogique',
                'questions': [
                    {
                        'texte': 'Le contenu de la formation correspondait-il à vos attentes ?',
                        'type': 'echelle', 'min': 1, 'max': 5,
                        'libelle_min': 'Pas du tout', 'libelle_max': 'Totalement',
                    },
                    {
                        'texte': 'Quels modules avez-vous trouvés les plus utiles ?',
                        'type': 'choix_multiple',
                        'choix': ['Modèles & migrations', 'Vues (CBV)', 'Templates', 'Formulaires', 'Admin Django', 'REST API'],
                    },
                    {
                        'texte': 'Niveau de difficulté perçu',
                        'type': 'choix_unique',
                        'choix': ['Trop facile', 'Adapté', 'Un peu difficile', 'Trop difficile'],
                    },
                ],
            },
            {
                'titre': 'Formateur & organisation',
                'questions': [
                    {
                        'texte': 'Évaluez la qualité de l\'enseignement',
                        'type': 'echelle', 'min': 1, 'max': 10,
                        'libelle_min': 'Mauvaise', 'libelle_max': 'Excellente',
                    },
                    {
                        'texte': 'Recommanderiez-vous cette formation ?',
                        'type': 'choix_unique',
                        'choix': ['Oui, sans hésitation', 'Oui, avec réserves', 'Non'],
                    },
                    {
                        'texte': 'Commentaires libres pour améliorer la formation',
                        'type': 'texte', 'obligatoire': False,
                    },
                ],
            },
        ],
    },
    {
        'titre': 'Préférences café du bureau',
        'description': 'Sondage rapide pour choisir la machine à café idéale !',
        'theme': 'chaleureux',
        'createur': 'ahmed.benali',
        'max_reponses': 50,
        'sections': [
            {
                'titre': 'Vos habitudes',
                'questions': [
                    {
                        'texte': 'Combien de cafés buvez-vous par jour au bureau ?',
                        'type': 'choix_unique',
                        'choix': ['Aucun', '1 café', '2-3 cafés', '4 cafés ou plus'],
                    },
                    {
                        'texte': 'Quel(s) type(s) de café préférez-vous ?',
                        'type': 'choix_multiple',
                        'choix': ['Espresso', 'Cappuccino', 'Latte', 'Café filtre', 'Thé', 'Chocolat chaud'],
                    },
                    {
                        'texte': 'Importance d\'une bonne machine à café pour votre bien-être au travail ?',
                        'type': 'echelle', 'min': 1, 'max': 5,
                        'libelle_min': 'Pas important', 'libelle_max': 'Indispensable',
                    },
                    {
                        'texte': 'Avez-vous une marque ou modèle de machine à recommander ?',
                        'type': 'texte', 'obligatoire': False,
                    },
                ],
            },
        ],
    },
    {
        'titre': 'Feedback site e-commerce',
        'description': 'Retours sur notre nouvelle plateforme en ligne.',
        'theme': 'defaut',
        'createur': 'marie.dupont',
        'est_archive': True,
        'sections': [
            {
                'titre': 'Expérience utilisateur',
                'questions': [
                    {
                        'texte': 'La navigation sur le site est-elle intuitive ?',
                        'type': 'echelle', 'min': 1, 'max': 10,
                        'libelle_min': 'Difficile', 'libelle_max': 'Très facile',
                    },
                    {
                        'texte': 'Avez-vous rencontré des problèmes techniques ?',
                        'type': 'choix_unique',
                        'choix': ['Non, aucun', 'Quelques ralentissements', 'Des erreurs fréquentes', 'Site inutilisable'],
                    },
                ],
            },
        ],
    },
    {
        'titre': 'Modèle : Satisfaction générale',
        'description': 'Modèle réutilisable pour sondages de satisfaction. Dupliquez et adaptez selon vos besoins.',
        'theme': 'professionnel',
        'createur': 'marie.dupont',
        'est_modele': True,
        'sections': [
            {
                'titre': 'Évaluation générale',
                'questions': [
                    {
                        'texte': 'Satisfaction globale (1 = très insatisfait, 10 = très satisfait)',
                        'type': 'echelle', 'min': 1, 'max': 10,
                        'libelle_min': 'Très insatisfait', 'libelle_max': 'Très satisfait',
                    },
                    {
                        'texte': 'Ce que vous avez le plus apprécié',
                        'type': 'texte', 'obligatoire': False,
                    },
                    {
                        'texte': 'Ce qui pourrait être amélioré',
                        'type': 'texte', 'obligatoire': False,
                    },
                    {
                        'texte': 'Recommanderiez-vous à votre entourage ?',
                        'type': 'choix_unique',
                        'choix': ['Oui, certainement', 'Peut-être', 'Non'],
                    },
                ],
            },
        ],
    },
]

# Réponses par sondage (index) et par visiteur
REPONSES_CONFIG = {
    0: ['jean.martin', 'sophie.l', 'youssef.k', 'leila.m'],   # satisfaction client
    1: ['jean.martin', 'youssef.k', 'leila.m'],                # bien-être
    2: ['sophie.l', 'youssef.k', 'jean.martin', 'leila.m'],   # formation django
    3: ['jean.martin', 'sophie.l', 'youssef.k', 'leila.m'],   # café (tous)
}

TEXTES_LIBRES = [
    "Très satisfait de l'expérience globale, rien à redire !",
    "Je suggère d'améliorer les délais de livraison.",
    "L'interface pourrait être plus intuitive.",
    "Excellent service, je recommande vivement.",
    "Quelques améliorations nécessaires côté support.",
    "Formation très complète, j'ai beaucoup appris.",
    "Le formateur était clair et pédagogue.",
    "Plus d'exercices pratiques seraient les bienvenus.",
    "Nespresso Vertuo, top pour les espressos !",
    "Une Senseo serait parfaite pour l'équipe.",
    "Je préfère le café filtre classique.",
    "L'ambiance dans l'équipe est vraiment bonne en général.",
    "Des sorties d'équipe régulières aideraient.",
    "Meilleure communication entre départements serait utile.",
]


class Command(BaseCommand):
    help = 'Remplit la base avec des données de test'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Creation des donnees de test ===\n'))

        users = self._creer_utilisateurs()
        sondages = self._creer_sondages(users)
        self._creer_reponses(users, sondages)
        self._afficher_bilan(users, sondages)

    # ─── Utilisateurs ─────────────────────────────────────────────────────────

    def _creer_utilisateurs(self):
        self.stdout.write('[1/3] Creation des utilisateurs...')
        users = {}
        for data in UTILISATEURS:
            user, created = Utilisateur.objects.get_or_create(
                username=data['username'],
                defaults={
                    'prenom': data['prenom'],
                    'nom': data['nom'],
                    'email': data['email'],
                    'password': PASSWORD,
                    'is_active': True,
                }
            )
            if created:
                profil, _ = Profil.objects.get_or_create(utilisateur=user)
                profil.role = data['role']
                profil.organisation = 'Entreprise Demo'
                profil.biographie = f'{data["prenom"]} {data["nom"]} - compte de demonstration'
                profil.save()
                self.stdout.write(f'   + {user.username} ({data["role"]})')
            else:
                self.stdout.write(f'   ~ {user.username} (existant)')
            users[data['username']] = user
        return users

    # ─── Sondages ─────────────────────────────────────────────────────────────

    def _creer_sondages(self, users):
        self.stdout.write('\n[2/3] Creation des sondages...')
        sondages = []

        for i, data in enumerate(SONDAGES_DATA):
            createur = users[data['createur']]

            sondage, created = Sondage.objects.get_or_create(
                titre=data['titre'],
                createur=createur,
                defaults={
                    'description': data.get('description', ''),
                    'theme': data.get('theme', 'defaut'),
                    'est_actif': not data.get('est_archive', False),
                    'est_anonyme': data.get('est_anonyme', False),
                    'est_modele': data.get('est_modele', False),
                    'est_archive': data.get('est_archive', False),
                    'duree_limite_minutes': data.get('duree_limite_minutes'),
                    'max_reponses': data.get('max_reponses'),
                }
            )

            if not created:
                self.stdout.write(f'   • {sondage.titre[:45]} (existant)')
                sondages.append(sondage)
                continue

            # Sections et questions
            all_choix_questions = []
            for s_idx, section_data in enumerate(data['sections']):
                section = SectionSondage.objects.create(
                    sondage=sondage,
                    titre=section_data['titre'],
                    ordre=s_idx,
                )
                for q_idx, q_data in enumerate(section_data['questions']):
                    question = Question.objects.create(
                        section=section,
                        texte=q_data['texte'],
                        type_question=q_data['type'],
                        est_obligatoire=q_data.get('obligatoire', True),
                        ordre=q_idx,
                        echelle_min=q_data.get('min', 1),
                        echelle_max=q_data.get('max', 10),
                        libelle_min=q_data.get('libelle_min', ''),
                        libelle_max=q_data.get('libelle_max', ''),
                    )
                    for c_idx, texte_choix in enumerate(q_data.get('choix', [])):
                        Choix.objects.create(question=question, texte=texte_choix, ordre=c_idx)
                    if q_data.get('type') in ('choix_unique', 'choix_multiple'):
                        all_choix_questions.append(question)

            # Logique conditionnelle : sondage bien-être
            if i == 1 and all_choix_questions:
                # Question "préciser difficultés" → liée au choix "Très insatisfait" ou "Insatisfait"
                try:
                    q_cond = Question.objects.get(
                        section__sondage=sondage,
                        texte__icontains='préciser'
                    )
                    q_source = Question.objects.get(
                        section__sondage=sondage,
                        texte__icontains='équilibre'
                    )
                    choix_insatisfait = Choix.objects.filter(
                        question=q_source,
                        texte__in=['Insatisfait', 'Très insatisfait']
                    ).first()
                    if choix_insatisfait:
                        q_cond.condition_choix = choix_insatisfait
                        q_cond.save()
                except Question.DoesNotExist:
                    pass

            sondages.append(sondage)
            if data.get('mot_de_passe'):
                flag = '[MDP]'
            elif data.get('est_archive'):
                flag = '[ARC]'
            elif data.get('est_modele'):
                flag = '[MOD]'
            else:
                flag = '[OK] '
            self.stdout.write(f'   {flag} {sondage.titre[:45]}')

        return sondages

    # ─── Réponses ─────────────────────────────────────────────────────────────

    def _creer_reponses(self, users, sondages):
        self.stdout.write('\n[3/3] Creation des reponses...')
        nb_reponses = 0

        for sondage_idx, usernames in REPONSES_CONFIG.items():
            if sondage_idx >= len(sondages):
                continue
            sondage = sondages[sondage_idx]
            if sondage.est_archive or sondage.est_modele:
                continue

            lien = sondage.liens.filter(est_actif=True).first()
            if not lien:
                continue

            questions = list(
                Question.objects.filter(section__sondage=sondage)
                .prefetch_related('choix')
                .order_by('section__ordre', 'ordre')
            )

            for username in usernames:
                user = users.get(username)
                if not user:
                    continue

                # Ne pas créer de doublon
                if Soumission.objects.filter(sondage=sondage, repondant=user, est_complete=True).exists():
                    continue

                # Créer la soumission avec une date aléatoire dans les 30 derniers jours
                jours_ago = random.randint(0, 30)
                heures_ago = random.randint(0, 23)
                commence_le = timezone.now() - timedelta(days=jours_ago, hours=heures_ago, minutes=random.randint(5, 30))
                termine_le = commence_le + timedelta(minutes=random.randint(2, 12))

                cle = hashlib.sha256(f"test_{sondage.pk}_{user.pk}".encode()).hexdigest()[:64]
                soumission = Soumission.objects.create(
                    sondage=sondage,
                    repondant=user,
                    adresse_ip='127.0.0.1',
                    cle_session=cle,
                    est_complete=True,
                    commence_le=commence_le,
                    termine_le=termine_le,
                )
                # Forcer les timestamps
                Soumission.objects.filter(pk=soumission.pk).update(
                    commence_le=commence_le, termine_le=termine_le
                )

                for question in questions:
                    reponse = Reponse.objects.create(soumission=soumission, question=question)

                    if question.type_question == Question.TYPE_TEXTE:
                        reponse.valeur_texte = random.choice(TEXTES_LIBRES)
                        reponse.save()

                    elif question.type_question == Question.TYPE_ECHELLE:
                        reponse.valeur_echelle = random.randint(question.echelle_min, question.echelle_max)
                        reponse.save()

                    elif question.type_question == Question.TYPE_CHOIX_UNIQUE:
                        choix_list = list(question.choix.all())
                        if choix_list:
                            choix = random.choice(choix_list)
                            reponse.save()
                            ReponseChoix.objects.create(reponse=reponse, choix=choix)

                    elif question.type_question == Question.TYPE_CHOIX_MULTIPLE:
                        choix_list = list(question.choix.all())
                        if choix_list:
                            nb = random.randint(1, min(3, len(choix_list)))
                            selectionnes = random.sample(choix_list, nb)
                            reponse.save()
                            for choix in selectionnes:
                                ReponseChoix.objects.create(reponse=reponse, choix=choix)

                nb_reponses += 1

                # Notification au créateur
                Notification.objects.get_or_create(
                    utilisateur=sondage.createur,
                    sondage=sondage,
                    message=f'Nouvelle réponse reçue pour « {sondage.titre} ».',
                    type_notification=Notification.TYPE_NOUVELLE_REPONSE,
                    defaults={'est_lu': random.choice([True, False])},
                )

        # Actualiser toutes les statistiques
        for sondage in sondages:
            stat, _ = StatistiqueSondage.objects.get_or_create(sondage=sondage)
            stat.actualiser()

        self.stdout.write(f'   + {nb_reponses} soumissions creees')

    # ─── Bilan ────────────────────────────────────────────────────────────────

    def _afficher_bilan(self, users, sondages):
        sep = '=' * 52
        self.stdout.write(self.style.SUCCESS('\nBase de donnees remplie avec succes !\n'))
        self.stdout.write(sep)
        self.stdout.write(f'  {"Identifiant":<22} {"Mot de passe":<14} Role')
        self.stdout.write(f'  {"-"*22} {"-"*14} {"-"*12}')
        self.stdout.write(f'  {"admin":<22} {"admin1234":<14} Admin (superuser)')
        for data in UTILISATEURS:
            self.stdout.write(f'  {data["username"]:<22} {"pass1234":<14} {data["role"].capitalize()}')
        self.stdout.write('')
        self.stdout.write(sep)
        for s in sondages:
            nb = s.soumission_set.filter(est_complete=True).count()
            if s.est_archive:
                statut = 'Archive'
            elif s.est_modele:
                statut = 'Modele'
            else:
                statut = f'{nb} reponse(s)'
            self.stdout.write(f'  {s.titre[:44]:<45} {statut}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('  Acces : http://127.0.0.1:8000'))
        self.stdout.write(sep + '\n')
