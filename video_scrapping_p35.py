import requests
from os.path import expanduser
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.common.by import By
import argparse

logger = logging.getLogger()
logger.setLevel('INFO')

class VideoScrapper():
    """A class to scrap data from Coursera's forums"""
    def __init__(self, mtp, email, courseName='python-machine-learning', time=30,
                 headless=False, destDir=None):
        """COURSE_NAME='python-plotting'  #'python-machine-learning' '  #villes-africaines-1"""
        self.mtp = mtp
        self.email = email
        self.course = courseName
        self.baseUrl = f"https://www.coursera.org/learn/{courseName}"
        self.destDir = destDir
        logger.info("Initialisation Driver Firefox")
        options = Options()
        if headless:
            options.add_argument('-headless')
        self.d = webdriver.Firefox(firefox_options=options)
        self.d.implicitly_wait(time)
        # suite. pour service à télécharger les vidéos si les urls sont compliquées
        #        self.get_week_url = week_url_generateur()

        logger.info(f"Initiatialization done with Implicite waiting time set to {time}")

    def find_elt_by(self, func, criteria):
        """fonctions qui raccourcis les codes pour accéder aux élements de la page web
        """
        if func == 'LINK':
            elt = self.d.find_element_by_link_text(criteria)
        elif func == 'CSS':
            elt = self.d.find_element_by_css_selector(criteria)
        elif func == 'ID':
            elt = self.d.find_element_by_id(criteria)
        elif func == 'TAG':
            elt = self.d.find_element_by_tag_name(criteria)
        return elt



#### Getting data from the threads ####

    def login(self):
        """log to coursera."""

        logger.info("Loging in")

        self.d.get("https://www.coursera.org/?authMode=login")

        # Logger in
        self.find_elt_by('CSS', "input[type=password]").clear()
        self.find_elt_by('CSS', "input[type=password]").send_keys(self.mtp)
        self.find_elt_by('CSS', "input[type=email]").clear()
        self.find_elt_by('CSS', "input[type=email]").send_keys(self.email)
        # Il y a plusieurs boutons caché pour les mobiles on les filtre donc
        elts = self.d.find_elements_by_css_selector('form button')
        button = [e for e in elts if 'Button' in e.get_attribute('class')][0]
        button.click()

        logger.info("Loging in Done !")
        return self.d

    def go_to(self, urlTail=None):
        """Va sur la page des semaines définie par l'urlTail
        """
        if urlTail is None:
            urlTail = self.get_week_url.next()

        self.d.get(f"https://www.coursera.org/learn/{self.course}/home/{urlTail}")

    def get_videos_url(self):
        """Une fois sur la page des semaines, récupère les urls des vidéos à télécharger
Enregistre ses urls dans la liste self.dwl"""
        listUrls = "div.od-lesson-collection-element a"
        elts = self.d.find_elements_by_css_selector(listUrls)

        # get all Video url from the list
        urls = [e.get_attribute('href') for e in elts if 'Video' in e.text]

        # filter only those that are lectures
        self.lectures = [url for url in urls if "lecture" in url]

        # on va parcourir les pages de lecture et on garde les links de téléchargement
        self.dwl = list()
        for lec in self.lectures:
            # On se déplace sur la page de la lecture
            self.d.get(lec)

            # On click sur le bouton de téléchargement
            self.d.find_element_by_css_selector("div.rc-DownloadsDropdown button").click()

            # on récupère le lien de téléchargement de la vidéo parmis les trois
            a_elts = self.d.find_elements_by_css_selector('div.rc-DownloadsDropdown a')
            dl_link = [a.get_attribute('href') for a in a_elts if 'mp4' in a.text][0]
            self.dwl.append(dl_link)

    def dl_videos(self, dwl=None, lectures=None, base_fn='videos', destDir=None):
        """Download the videos lectures once their urls was retreived"""
        if not dwl:
            dwl = self.dwl

        if not lectures:
            lectures = self.lectures

        if destDir is None and self.destDir is None:
            home = expanduser("~")
            self.destDir = f'{home}/Videos/Coursera/'

        # générons les noms des fichiers
        fns = ["%s_%s.mp4" % (base_fn, fn.split('/')[-1]) for fn in lectures]

        logger.info(f"Se prépare à télécharger {len(fns)} files")
        for i in range(len(fns)):
            logger.info(f"Downloading file : {fns[i]} -->", end=" ")
            r = requests.get(dwl[i], stream=True)
            rlen = int(r.headers['Content-length'])
            # on sauvegarde les fichiers en format binaire
            with open(self.destDir+fns[i], 'xb') as fd:
                j = 0
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
                    j += 1
                    dpercent = round(j*len(chunk)/rlen * 100)
                    print(f"Got {j*len(chunk)}/{rlen}  ({dpercent}%)", end='\r')

                logger.info("\nDone")

            print(f"Finished dowloading the {i+1} file out of {len(fns)}")

    def close(self):
        d.close()

    ################ RUN ################

    def run(self, wStart, wEnd):
        d = vs.login()
        s = input('Captcha terminé ?  Continuer le téléchargement ? Répondre yes (y) ou oui (o)')
        if s.lower() in ['y', 'yes', 'o', 'oui']:
            for i in range(wStart, wEnd+1):
                logger.info(f"Starting Loop {i}")
                self.go_to(urlTail=f"week/{i}")
                # créer une liste des urls à télécharger (dans self.dwl)
                self.get_videos_url()
                # retour à la home page du cours
                self.go_to("")
                self.dl_videos(base_fn=f"week{i}_video")
                logger.info(f"Loop {i} Done !")
        else:
            logger.warning('Annuler')
        d.close()


################ getting the args ################

def get_args():
    """Parse the function's arguments"""
    description = '''Un bot pour télécharger les vidéos d'un cours de coursera.'''
    time_help = "Le temps d'attente pour la réponse des pages web avant que le bot n'abandonne"
    courseName_help = "*Nom du cours (voir l'url) par exemple: python-machine-learning"
    email_help = "*l'email utiliser pour se connecter à Coursera"
    mtp_help = "*Le mot de passe pour Coursera"
    week_help = "l'interval des numéros des week à télécharger. Défault 1 à 4"
    headless_help = "Si il faut ouvrir le navigateur du bot ou le faire tourner en fond, par default le navigateur se lance visuellement"
    destDir_help = "Le dossier de destination des vidéo téléchargées. (Default ~/Videos/Coursera/)"

    # create the parser
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--mtp', '-p', type=str, help=mtp_help, required=True)
    parser.add_argument('--email', '-e', type=str, help=email_help, required=True)
    parser.add_argument('--courseName', '-c', type=str, help=courseName_help, required=True)
    parser.add_argument('--time', '-t', type=int, default=60, help=time_help)
    parser.add_argument('--week', '-w', type=int, nargs=2, default=[1, 4], help=week_help)
    parser.add_argument('--destDir', '-d', type=str, help=destDir_help)
    parser.add_argument('--headless', '-H', action="store_true", help=headless_help)

    return parser.parse_args()


if __name__ == "__main__":
    print("Programme to download coursera's videos")
    args = get_args()
    kwargs = {
        'mtp': args.mtp,
        'email': args.email,
        'courseName': args.courseName,
        'time': args.time,
        'headless': args.headless,
        'destDir': args.destDir,
    }
    vs = VideoScrapper(**kwargs)
    vs.run(*args.week)



################ divers ################

# def week_url_generateur(nb_weeks=10):
#     """génère les url des semaines successives, mais pas utile dans le cas simple."""
#     for i in range(nb_weeks-1):
#         yield 'week/%s' % (i+1)
