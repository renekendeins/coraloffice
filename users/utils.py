
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime

class EmailTranslations:
    TRANSLATIONS = {
        'EN': {
            'dive_reminder_subject': 'Dive Activity Reminder',
            'welcome_subject': 'Welcome to CIPS!',
            'dive_reminder': {
                'greeting': 'Hello!',
                'reminder_text': 'This is a friendly reminder about your upcoming dive activity:',
                'activity': 'Activity',
                'date': 'Date',
                'time': 'Time',
                'dive_site': 'Dive Site',
                'important_notes': 'Important Notes',
                'what_to_bring': 'What to Bring',
                'bring_items': [
                    'Valid diving certification (if applicable)',
                    'Swimming suit',
                    'Towel',
                    'Sunscreen',
                    'Any personal diving equipment you prefer to use'
                ],
                'boat_info': [
                    '📍 The meeting point is at the Timba dock',
                    '🛥 Boat: Catamaran - Maca III',
                    '🕒 To streamline activities, payment must be made before starting',
                    '🚿 The boat has a rinsing area, restroom, and lift'
                ],
                'arrival_info': 'Please arrive 30 minutes before the scheduled time for equipment fitting and briefing.',
                'contact_info': 'If you have any questions or need to make changes, please contact us.',
                'looking_forward': 'We look forward to diving with you!',
                'best_regards': 'Best regards',
                'team': 'The CIPS Team'
            },
            'welcome': {
                'greeting': ' Hello and welcome to CIPS!',
                'thank_you': 'Thank you for completing your medical form. We have received your information and our team will review it shortly.',
                'next_steps': 'What happens next?',
                'review_process': 'Our certified diving professionals will review your medical form to ensure your safety.',
                'contact_soon': 'We will contact you soon to schedule your diving activities.',
                'reminders': 'You will receive email reminders before each scheduled activity with all the details you need.',
                'questions': 'If you have any immediate questions or concerns, please don\'t hesitate to contact us.',
                'excited': 'We are excited to share the underwater world with you!',
                'best_regards': 'Best regards',
                'team': 'The CIPS Team'
            }
        },
        'ES': {
            'dive_reminder_subject': 'Recordatorio de Actividad de Buceo',
            'welcome_subject': '¡Bienvenido a CIPS!',
            'dive_reminder': {
                'greeting': '¡Hola!',
                'reminder_text': 'Este es un recordatorio amistoso sobre tu próxima actividad de buceo:',
                'activity': 'Actividad',
                'date': 'Fecha',
                'time': 'Hora',
                'dive_site': 'Punto de Buceo',
                'important_notes': 'Notas Importantes',
                'what_to_bring': 'Qué Traer',
                'bring_items': [
                    'Certificación de buceo válida (si aplica)',
                    'Seguro de buceo (si aplica)',
                    'Revisión (si aplica)',
                    'Traje de baño y toalla (recomendado)',
                    'Protector solar (recomendado) ',
                    'Cualquier equipo de buceo personal que prefieras usar'
                ],
                'boat_info':[
                    '📍 El punto de encuentro es en el muelle de la Timba',
                    '🛥 Barco: Catamarán - Maca III',
                    '🕒 Para agilizar las actividades el pago se debe hacer antes de empezar',
                    '🚿 Disponemos de zona de desalado, baño y ascensor en el barco'
                ],
                'arrival_info': 'Por favor llega 30 minutos antes de la hora programada para el ajuste del equipo y la explicación.',
                'contact_info': 'Si tienes alguna pregunta o necesitas hacer cambios, por favor contáctanos.',
                'looking_forward': '¡Esperamos bucear contigo!',
                'best_regards': 'Saludos cordiales',
                'team': 'El Equipo de CIPS'
            },
            'welcome': {
                'greeting': '¡Bienvenido a CIPS!',
                'thank_you': 'Gracias por completar tu formulario médico. Hemos recibido tu información y nuestro equipo la revisará en breve.',
                'next_steps': '¿Qué sigue?',
                'review_process': 'Nuestros profesionales certificados de buceo revisarán tu formulario médico para asegurar tu seguridad.',
                'contact_soon': 'Te contactaremos pronto para programar tus actividades de buceo.',
                'reminders': 'Recibirás recordatorios por email antes de cada actividad programada con todos los detalles que necesitas.',
                'questions': 'Si tienes alguna pregunta o inquietud inmediata, no dudes en contactarnos.',
                'excited': '¡Estamos emocionados de compartir el mundo submarino contigo!',
                'best_regards': 'Saludos cordiales',
                'team': 'El Equipo de CIPS'
            }
        },
        'FR': {
            'dive_reminder_subject': 'Rappel d\'Activité de Plongée',
            'welcome_subject': 'Bienvenue chez CIPS!',
            'dive_reminder': {
                'greeting': 'Bonjour!',
                'reminder_text': 'Ceci est un rappel amical concernant votre prochaine activité de plongée:',
                'activity': 'Activité',
                'date': 'Date',
                'time': 'Heure',
                'dive_site': 'Site de Plongée',
                'important_notes': 'Notes Importantes',
                'what_to_bring': 'Quoi Apporter',
                'bring_items': [
                    'Certification de plongée valide (si applicable)',
                    'Maillot de bain',
                    'Serviette',
                    'Crème solaire',
                    'Tout équipement de plongée personnel que vous préférez utiliser'
                ],
                'boat_info': [
                    '📍 Le point de rendez-vous est au quai de la Timba',
                    '🛥 Bateau : Catamaran - Maca III',
                    '🕒 Pour faciliter les activités, le paiement doit être effectué avant le début',
                    '🚿 Nous disposons d’une zone de rinçage, de toilettes et d’un ascenseur à bord'
                ],

                'arrival_info': 'Veuillez arriver 30 minutes avant l\'heure prévue pour l\'ajustement de l\'équipement et le briefing.',
                'contact_info': 'Si vous avez des questions ou devez apporter des modifications, veuillez nous contacter.',
                'looking_forward': 'Nous avons hâte de plonger avec vous!',
                'best_regards': 'Meilleures salutations',
                'team': 'L\'Équipe de CIPS'
            },
            'welcome': {
                'greeting': 'Bienvenue chez CIPS!',
                'thank_you': 'Merci d\'avoir complété votre formulaire médical. Nous avons reçu vos informations et notre équipe les examinera sous peu.',
                'next_steps': 'Que se passe-t-il ensuite?',
                'review_process': 'Nos professionnels certifiés de plongée examineront votre formulaire médical pour assurer votre sécurité.',
                'contact_soon': 'Nous vous contacterons bientôt pour programmer vos activités de plongée.',
                'reminders': 'Vous recevrez des rappels par email avant chaque activité programmée avec tous les détails dont vous avez besoin.',
                'questions': 'Si vous avez des questions ou préoccupations immédiates, n\'hésitez pas à nous contacter.',
                'excited': 'Nous sommes ravis de partager le monde sous-marin avec vous!',
                'best_regards': 'Meilleures salutations',
                'team': 'L\'Équipe de CIPS'
            }
        },
        'CAT': {
            'dive_reminder_subject': 'Recordatori d\'Activitat de Busseig',
            'welcome_subject': 'Benvingut a CIPS!',
            'dive_reminder': {
                'greeting': 'Hola!',
                'reminder_text': 'Aquest és un recordatori amistós sobre la teva propera activitat de busseig:',
                'activity': 'Activitat',
                'date': 'Data',
                'time': 'Hora',
                'dive_site': 'Punt de Busseig',
                'important_notes': 'Notes Importants',
                'what_to_bring': 'Què Portar',
                'bring_items': [
                    'Certificació de busseig vàlida (si escau)',
                    'Banyador',
                    'Tovallola',
                    'Protector solar',
                    'Qualsevol equip de busseig personal que prefereixis usar'
                ],
                'boat_info': [
                    '📍 El punt de trobada és al moll de la Timba',
                    '🛥 Vaixell: Catamarà - Maca III',
                    '🕒 Per agilitzar les activitats, el pagament s’ha de fer abans de començar',
                    '🚿 Disposem de zona de dessalació, bany i ascensor al vaixell'
                ],

                'arrival_info': 'Si us plau, arriba 30 minuts abans de l\'hora programada per a l\'ajust de l\'equip i l\'explicació.',
                'contact_info': 'Si tens alguna pregunta o necessites fer canvis, si us plau contacta\'ns.',
                'looking_forward': 'Esperem bussejar amb tu!',
                'best_regards': 'Salutacions cordials',
                'team': 'L\'Equip de CIPS'
            },
            'welcome': {
                'greeting': 'Benvingut a CIPS!',
                'thank_you': 'Gràcies per completar el teu formulari mèdic. Hem rebut la teva informació i el nostre equip la revisarà aviat.',
                'next_steps': 'Què passa ara?',
                'review_process': 'Els nostres professionals certificats de busseig revisaran el teu formulari mèdic per assegurar la teva seguretat.',
                'contact_soon': 'Et contactarem aviat per programar les teves activitats de busseig.',
                'reminders': 'Rebràs recordatoris per email abans de cada activitat programada amb tots els detalls que necessites.',
                'questions': 'Si tens alguna pregunta o preocupació immediata, no dubtis a contactar-nos.',
                'excited': 'Estem emocionats de compartir el món submarí amb tu!',
                'best_regards': 'Salutacions cordials',
                'team': 'L\'Equip de CIPS'
            }
        },
        'DE': {
            'dive_reminder_subject': 'Tauchaktivitäts-Erinnerung',
            'welcome_subject': 'Willkommen bei CIPS!',
            'dive_reminder': {
                'greeting': 'Hallo!',
                'reminder_text': 'Dies ist eine freundliche Erinnerung an Ihre bevorstehende Tauchaktivität:',
                'activity': 'Aktivität',
                'date': 'Datum',
                'time': 'Zeit',
                'dive_site': 'Tauchplatz',
                'important_notes': 'Wichtige Hinweise',
                'what_to_bring': 'Was mitbringen',
                'bring_items': [
                    'Gültige Tauchzertifizierung (falls zutreffend)',
                    'Badeanzug',
                    'Handtuch',
                    'Sonnencreme',
                    'Jede persönliche Tauchausrüstung, die Sie bevorzugen'
                ],
                'boat_info': [
                    '📍 Treffpunkt ist am Steg von Timba',
                    '🛥 Boot: Katamaran - Maca III',
                    '🕒 Zur Beschleunigung der Aktivitäten muss die Zahlung vor Beginn erfolgen',
                    '🚿 An Bord gibt es eine Spülzone, eine Toilette und einen Aufzug'
                ],

                'arrival_info': 'Bitte kommen Sie 30 Minuten vor der geplanten Zeit für die Ausrüstungsanpassung und das Briefing.',
                'contact_info': 'Wenn Sie Fragen haben oder Änderungen vornehmen müssen, kontaktieren Sie uns bitte.',
                'looking_forward': 'Wir freuen uns darauf, mit Ihnen zu tauchen!',
                'best_regards': 'Mit freundlichen Grüßen',
                'team': 'Das CIPS Team'
            },
            'welcome': {
                'greeting': 'Willkommen bei CIPS!',
                'thank_you': 'Vielen Dank für das Ausfüllen Ihres medizinischen Formulars. Wir haben Ihre Informationen erhalten und unser Team wird sie in Kürze überprüfen.',
                'next_steps': 'Was passiert als nächstes?',
                'review_process': 'Unsere zertifizierten Tauchprofis werden Ihr medizinisches Formular überprüfen, um Ihre Sicherheit zu gewährleisten.',
                'contact_soon': 'Wir werden Sie bald kontaktieren, um Ihre Tauchaktivitäten zu planen.',
                'reminders': 'Sie erhalten E-Mail-Erinnerungen vor jeder geplanten Aktivität mit allen Details, die Sie benötigen.',
                'questions': 'Wenn Sie sofortige Fragen oder Bedenken haben, zögern Sie nicht, uns zu kontaktieren.',
                'excited': 'Wir freuen uns darauf, die Unterwasserwelt mit Ihnen zu teilen!',
                'best_regards': 'Mit freundlichen Grüßen',
                'team': 'Das CIPS Team'
            }
        },
        'NL': {
            'dive_reminder_subject': 'Herinnering: Duikactiviteit',
            'welcome_subject': 'Welkom bij CIPS!',
            'dive_reminder': {
                'greeting': 'Hallo!',
                'reminder_text': 'Dit is een vriendelijke herinnering aan je aankomende duikactiviteit:',
                'activity': 'Activiteit',
                'date': 'Datum',
                'time': 'Tijd',
                'dive_site': 'Duiklocatie',
                'important_notes': 'Belangrijke opmerkingen',
                'what_to_bring': 'Wat mee te nemen',
                'bring_items': [
                    'Geldige duikbrevet (indien van toepassing)',
                    'Zwemkleding',
                    'Handdoek',
                    'Zonnebrandcrème',
                    'Eigen duikmateriaal (indien gewenst)'
                ],
                'boat_info': [
                    '📍 De ontmoetingsplek is bij de Timba steiger',
                    '🛥 Boot: Catamaran - Maca III',
                    '🕒 Om de activiteiten te versnellen, moet de betaling vooraf worden gedaan',
                    '🚿 Er is een spoelzone, toilet en lift aan boord'
                ],
                'arrival_info': 'Kom alstublieft 30 minuten voor de geplande tijd aan voor het passen van de uitrusting en de briefing.',
                'contact_info': 'Als je vragen hebt of wijzigingen wilt aanbrengen, neem dan contact met ons op.',
                'looking_forward': 'We kijken ernaar uit om samen met jou te duiken!',
                'best_regards': 'Met vriendelijke groet',
                'team': 'Het CIPS-team'
            },
            'welcome': {
                'greeting': 'Hallo en welkom bij CIPS!',
                'thank_you': 'Bedankt voor het invullen van je medische formulier. We hebben je gegevens ontvangen en ons team zal deze spoedig bekijken.',
                'next_steps': 'Wat gebeurt er nu?',
                'review_process': 'Onze gecertificeerde duikprofessionals zullen je medische formulier beoordelen om je veiligheid te garanderen.',
                'contact_soon': 'We nemen binnenkort contact met je op om je duikactiviteiten in te plannen.',
                'reminders': 'Je ontvangt e-mailherinneringen vóór elke geplande activiteit met alle benodigde informatie.',
                'questions': 'Heb je direct vragen of zorgen, neem dan gerust contact met ons op.',
                'excited': 'We zijn enthousiast om de onderwaterwereld met je te delen!',
                'best_regards': 'Met vriendelijke groet',
                'team': 'Het CIPS-team'
            }
        },

    }

    @classmethod
    def get_translation(cls, language, key, **kwargs):
        """Get translated text for a given language and key"""
        # Default to English if language not found
        lang_dict = cls.TRANSLATIONS.get(language, cls.TRANSLATIONS['EN'])
        
        # Navigate through nested keys
        text = lang_dict
        for k in key.split('.'):
            text = text.get(k, '')
            if not text:
                # Fallback to English
                text = cls.TRANSLATIONS['EN']
                for k in key.split('.'):
                    text = text.get(k, '')
                break
        
        if isinstance(text, str) and kwargs:
            return text.format(**kwargs)
        return text


def send_dive_reminder_email(customer, dive_schedule, course):
    """Send a dive reminder email to the customer"""
    try:
        # Get customer's preferred language
        language = customer.language or 'EN'
        
        # Get diving center name
        diving_center_name = customer.diving_center.userprofile.business_name or customer.diving_center.username

        # Prepare context for email template
        context = {
            'customer': customer,
            'dive_schedule': dive_schedule,
            'course': course,
            'diving_center_name': diving_center_name,
            'language': language,
            'translations': EmailTranslations.get_translation(language, 'dive_reminder'),
        }
        
        # Get translated subject
        subject = EmailTranslations.get_translation(
            language, 
            'dive_reminder_subject', 
            course_name=course.name
        )
        
        # Render email templates
        html_message = render_to_string('users/emails/dive_reminder.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending dive reminder email: {e}")
        return False


def send_welcome_email(customer):
    """Send a welcome email after medical form submission"""
    try:
        # Get customer's preferred language
        language = customer.language or 'EN'
        print('language',language)
        
        # Get diving center name
        diving_center_name = 'CIPS'

        print('customer', customer)
        # Prepare context for email template
        context = {
            'customer': customer,
            'diving_center_name': 'CIPS',
            'language': language,
            'translations': EmailTranslations.get_translation(language, 'welcome', 
                                                            customer_name=customer.get_full_name(), 
                                                            diving_center=diving_center_name),
        }
        print('context',context)
        
        # Get translated subject
        subject = EmailTranslations.get_translation(
            language, 
            'welcome_subject', 
            diving_center=diving_center_name
        )
        print('subject',subject)
        
        # Render email templates
        html_message = render_to_string('users/emails/welcome.html', context)
        print('html_message', html_message)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
