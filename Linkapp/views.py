from django.shortcuts import render, redirect
from django.http import HttpResponse
from Linkapp.models import ScrapedData1
import random as rd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from Linkapp.mods import subparts
from Linkapp.connection_configs import slinkrconnect
from selenium.webdriver.common.by import By
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from Linkapp.forms import Registerform
from selenium.webdriver.common.keys import Keys
from time import sleep, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from Linkapp.models import CompanyData1
from Linkapp.models import EmployeeDetail1
import re
from django.db.models import Q
from django.contrib import messages

# from django.core.files import File
# import csv
# import os


# Connection to the automation account and return the driver
driver = slinkrconnect()


def dashboard(request):
    if request.user.username:
        uname = request.user.username
        return render(request, "Linkapp/index1.html", {'uname': uname})
    else:
        return redirect('/login')
   
def dashboard1(request):
    if request.user.username:
        uname=request.user.username
        return render(request,"Linkapp/company.html",{'uname':uname})  
#    i changed html file
    else:
         return redirect('/login')


def scrape(request):
    url = request.POST['link']
    print(url)
    
    try:
        print("Now started")
        # person_data = ScrapedData1.objects.get(Q(profile_url__iexact=url))
        person_data = ScrapedData1.objects.filter(profile_url=url).first()
        exp1=person_data.exp
        print("Raw exp data:",exp1)
        raw_exp_data=''.join(exp1)
        
        exp_str = re.sub(r'[^a-zA-Z0-9\s]', '', raw_exp_data)
        print("Processed exp data:", exp_str)
        
       
        content = {
            'profile_url': person_data.profile_url,
            'name': person_data.name,
            'works_at': person_data.works_at,
            'location': person_data.location,
            # 'exp': eval(person_data.exp),
            # 'exp': person_data.exp,
            'exp': exp_str,
            'about': person_data.about,
            'uname': person_data.uname,
            # 'education': eval(person_data.education),
            'education': person_data.education,
        }
        
        return render(request, 'Linkapp/index1.html', content)
    except Exception:
        profile_url = url
        driver.get(profile_url)
        start = time()
        initialScroll = 0
        finalScroll = 1000
        while True:
            driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            initialScroll = finalScroll
            finalScroll += 1000
            sleep(rd.randint(2, 7))
            end = time()
            if round(end - start) > rd.randint(5, 9):
                break
        src = driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        content = {}
        try:
            intro = soup.find('div', {'class': 'pv-text-details__left-panel'})
            name_loc = intro.find("h1")
            name = name_loc.get_text().strip()
            works_at_loc = intro.find("div", {'class': 'text-body-medium'})
            works_at = works_at_loc.get_text().strip()
            print("Name -->", name,
                "\nWorks At -->", works_at, )
            loc = soup.find('span', {'class': 'text-body-small inline t-black--light break-words'})
            locat = loc.get_text().strip()
            print("Location -->", locat)
            experience = soup.find("div", {"class": "pvs-list__outer-container"}).find('ul')
            if experience:
                experience = experience.find_all('div', {'class': 'display-flex flex-column full-width align-self-center'})
                exskill = []
                for i in experience:
                        exskill.append(i.find_all('span', {'class': 'visually-hidden'}))
                explist = []
                for i in exskill:
                        for j in i:
                            explist.append(j.get_text().strip())
                print("EXPERIENCELIST: ", explist)
            else:
                explist = ["Fresher"]  # Set experiencelist to an empty list if experience is None
                print("EXPERIENCELIST is empty.")
            # About data
            about = soup.find('div', {'class': 'display-flex full-width'}).find('span', {'class': 'visually-hidden'})
            about = about.get_text()
            # ALl other data xp -"//section[contains(@id, 'ember')]/div[@class='pvs-header__container' and @class='pvs-list__outer-container']/ul//span[@class='visually-hidden']
            other_info = driver.find_elements(By.XPATH,
                                            "//section[contains(@id, 'ember')]/div[@class='pvs-header__container' or  @class='pvs-list__outer-container' ]//span[@class='visually-hidden']")
            ind = []
            for e in other_info:
                ind.append(e.text.strip())
            print(ind)
            education = subparts(ind, 'Education', 'person')
            certificates = subparts(ind, 'Certficates', 'person')
            projects = subparts(ind, 'Projects', 'person')
            '''education=education.find_all('div',{'class':'display-flex flex-column full-width align-self-center'})
                edu=[]
                for i in education:
                    edu.append(i.find_all('span',{'class':'visually-hidden'}))  
                edulist=[]
                for i in edu:
                    for j in i:
                        edulist.append(j.get_text().strip())
                print('EDU LIST VAR :',edulist)'''
            content['profile_url']=profile_url
            content['name'] = name
            content['works_at'] = works_at
            content['location'] = locat
            content['exp'] = explist
            content['about'] = about
            content['uname'] = request.user.username
            content['edu'] = education
            content['cert'] = certificates
            content['proj'] = projects
            
            scraped_data = ScrapedData1(
            profile_url=profile_url,
            name=name,
            works_at=works_at,
            location=locat,
            # exp="".join(explist),
            exp=explist,
            about=about,
            uname=request.user.username,
            education=education,)
            
            scraped_data.save()
            messages.success(request,"Your message has been successfully sent")
            return render(request, 'Linkapp/index1.html', content)
        
        except Exception as e:

            return redirect('/home')


def register(request):
    if request.method == 'POST':
        frmdata = Registerform(request.POST)
        if frmdata.is_valid():
            frmdata.save()
            
            return redirect('/login')
        else:
            messages.error(request,"Invaild Data")
            return redirect('/register')
    else:
        regform = Registerform()
        return render(request, 'Linkapp/register1.html', {'regform': regform})


def user_login(request):
    if request.method == 'POST':
        logform = AuthenticationForm(request=request, data=request.POST)
        if logform.is_valid():
            uname = logform.cleaned_data['username']
            passw = logform.cleaned_data['password']
            u = authenticate(username=uname, password=passw)
            print('VAriable u', u)
            if u:
                login(request, u)
                return redirect('/home')
            else:
                return render(request, 'Linkapp/login1.html', {'logform': logform, 'msg': 'Username or password incorrect'})
        else:
            logform = AuthenticationForm()
            return render(request, 'Linkapp/login1.html', {'logform': logform, 'msg': 'Username or password incorrect'})

    else:
        logform = AuthenticationForm()
        return render(request, 'Linkapp/login1.html', {'logform': logform})


def user_logout(request):
    logout(request)
    return redirect('/login')


def companysearch(request):
    return render(request, 'Linkapp/company.html')




def searchcomp(request):
    s = request.POST['search']
    lo=s.lower()
    print(lo)
    sleep(1)
    try:
       
        # comp_na=  CompanyData1.objects.get(comp_name).lower()
        # print(comp_na)
        # scrap_com=s.lower()
        # company_data = CompanyData1.objects.get(comp_name=lo)
        # company_data = CompanyData1.objects.get(Q(comp_name__iexact=lo))
        company_data = CompanyData1.objects.get(Q(comp_name__icontains=lo))
        print('1111')
        

        

        # If data exists, retrieve it from the database
        # 
        employees = EmployeeDetail1.objects.filter(company=company_data)
        print(employees)
        # Create a dictionary to hold the data

        com_na=company_data.comp_name.lower()

        # person_data = ScrapedData1.objects.filter(profile_url=url).first()
        # exp1=person_data.exp
        # print("Raw exp data:",exp1)
        # raw_exp_data=''.join(exp1)
        
        # exp_str = re.sub(r'[^a-zA-Z0-9\s]', '', raw_exp_data)
        # print("Processed exp data:", exp_str)

        comp_size=company_data.company_size
        raw_comp_size=''.join(comp_size)
        # comp_str = re.sub(r'[^a-zA-Z0-9\s]', '', raw_comp_size)
        comp_str = re.sub(r'[^a-zA-Z0-9\s-]', '', raw_comp_size)

       
        
        content = {
            'company_name': com_na,

            'followers': company_data.foll,
            'website': company_data.website,
            'industry': company_data.industry,
            'company_size': comp_str,
            'headquarter': company_data.headquarter,
            'founded': company_data.founded,
            'specialties': company_data.specialties,

            'emp_info': [(employee.e_name, employee.e_head, employee.e_link) for employee in employees],
        }
        messages.success(request,"Your message has been successfully fetched from Database")
        return render(request, 'Linkapp/company.html', content)
    # except CompanyData1.DoesNotExist:
    except Exception:
        # search = driver.find_element(By.CLASS_NAME, 'search-global-typeahead__input')
        # search = driver.find_element(By.XPATH, "//input[contains(@class, 'search-global-typeahead__input')]")
        search = driver.find_element(By.XPATH, "//div[contains(@id, 'global-nav-typeahead')]/input")
        print(1)
        sleep(1)
        driver.execute_script("arguments[0].click();", search)
        print(2)
        sleep(1)
        # search.send_keys(s)
        driver.execute_script("arguments[0].value = '" + s + "' ", search)
        print(3)
        sleep(1)
        # search.send_keys(Keys.ENTER)
        # driver.execute_script("arguments[0].dispatchEvent(new Event('keydown', { 'key': 'Enter' }))", search)
        driver.execute_script(
            "var event = new KeyboardEvent('keydown', {'key':'Enter'}); arguments[0].dispatchEvent(event);", search)
        print(4)
        sleep(3)
        # search.clear()
        # print(5)
        # sleep(5)
        # search_ck = driver.find_element(By.XPATH,
        #                                 "//div[contains(@class, 'search-nec__hero-kcard-v2-content t-black')]/div/div[contains(@class, 'search-nec__hero')]")

        ## search_ck.click()
        ## driver.execute_script("arguments[0].click();", search_ck)

        try:
            lk = driver.find_element(By.XPATH, "//div[contains(@class, 'search-nec__hero')]//a[contains(@class, 'app-aware-link')]")
            comp_lk = lk.get_attribute('href')
            driver.get(comp_lk + 'about')
        except Exception as e:
            print('Hello')
            # driver.get('www.google.com')
            driver.execute_script("window.open('https://www.google.com');")
            driver.switch_to.window(driver.window_handles[1])
            search_bar_loc = driver.find_element(By.XPATH, "//textarea[contains(@type, 'search')]")
            search_bar_loc.send_keys(s + "linkedin link")
            search_bar_loc.send_keys(Keys.ENTER)
            search_data_loc = driver.find_element(By.XPATH, "//div[contains(@id, 'res')]/div[contains(@id, 'search')]//a")
            comp_google_lk = search_data_loc.get_attribute('href')
            print(comp_google_lk)
            if re.search('www', comp_google_lk):
                comp_lk = comp_google_lk + '/'
            else:
                comp_lk = re.sub('in', 'www', comp_google_lk, 1)+'/'
            sleep(1)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            sleep(2)
            driver.get(comp_lk + 'about')
            sleep(2)
            print(4.1)
            # comp_lk = driver.find_element(By.XPATH, "//nav[contains(@class, 'org-page')]//li[2]/a")
            # driver.execute_script("arguments[0].click();", comp_lk)
            # print(4.2)

        ## action = ActionChains(driver)
        ## action.click(search_ck).perform()
        ## print(6)
        ## print(driver.current_url)
        ## sleep(5)
        ## search_about = driver.find_element(By.XPATH, "//nav/ul[contains(@class, 'org-page-navigation')]/li[2]/a")

        ## search_about.click()
        ## driver.execute_script("arguments[0].click();", search_about)


        sleep(3)
        print(7)

        ## driver.find_element(By.CLASS_NAME, 'reusable-search__entity-result-list list-style-none').click()
        ## driver.find_element(By.ID, 'ember2817').click()
        ## page_source = driver.execute_script("return document.documentElement.innerHTML")
        ## print(page_source)
        ##
        ## url = request.POST['search']
        ## print(url)
        ## driver.get(url + 'about')

        start = time()
        initialScroll = 0
        finalScroll = 1000
        while True:
            driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            initialScroll = finalScroll
            finalScroll += 1000
            sleep(rd.randint(2, 7))
            end = time()
            if round(end - start) > rd.randint(5, 9):
                break
        src = driver.page_source
        # print(src)
        soup = BeautifulSoup(src, 'lxml')
        content = {}
        try:
            comp_name_loc = soup.find('div', {'class': 'block mt2'}).find('h1')
            comp_name = comp_name_loc.get_text().strip()
            print(comp_name_loc.get_text(), comp_name)

            foll_loc = soup.find('div', 'org-top-card-summary-info-list').find('div', 'inline-block')
            a = foll_loc.get_text().strip()
            b = a.replace('\n', '-').split('-')
            print(b)
            foll = ''
            for i in b:
                if 'followers' in i:
                    foll = i.strip()

            about_loc = driver.find_element(By.XPATH, "//div[@class='org-grid__content-height-enforcer']/div["
                                                    "@class='mb6']/div/div[contains(@id, 'ember')]/section")

            about = about_loc.text.split('\n')
            
            website=subparts(about, 'Website', 'company')[0]
            industry=subparts(about, 'Industry', 'company')[0]
            company_size=subparts(about, 'Company size', 'company')[0]
            headquarter=subparts(about, 'Headquarters', 'company')[0]
            founded=subparts(about, 'Founded', 'company')[0]
            specialties=subparts(about, 'Specialties', 'company')[0]
            employees=comp_emp_data(comp_lk)




            print(about)
            content['company_name'] = comp_name
            content['followers'] = foll

            content['website'] = website
            content['industry'] = industry
            content['company_size'] = company_size
            print(content['company_size'])
            content['headquarter'] = headquarter
            print(content['headquarter'])
            content['founded'] = founded
            print(content['founded'])
            content['specialties'] = specialties
            print(content['specialties'])
            print(comp_lk)
            content['emp_info'] = employees
                
                


            company_data = CompanyData1(
            comp_name=comp_name,
            website=website,
            industry=industry,
            # exp="\n".join(explist),
            # company_size='\n'.join(company_size),
            company_size=company_size,
            headquarter=headquarter,
            founded=founded,
            foll=foll,
            specialties=specialties,
            )
            company_data.save()

            for emp_info in employees:
                # print(emp_info,len(emp_info),"#######")
                if emp_info[0]!= "LinkedIn Member" and len(emp_info)>=3 and len(emp_info[0])<=20:
                    employee_data= EmployeeDetail1(
                    # compy_name=comp_name,
                    e_name=emp_info[0],
                    e_head=emp_info[1],
                    e_link=emp_info[-1],
                    company=company_data,
                    )
        
                    employee_data.save()


            
            messages.success(request,"Your data has been successfully stored to Database")
            return render(request, 'Linkapp/company.html', content)
        except Exception as e:
            redirect('/company')


def comp_emp_data(url):
    driver.get(url + 'people')
    sleep(3)

    # start = time()
    # initialScroll = 0
    # finalScroll = 1000
    # while True:
    #     driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
    #     initialScroll = finalScroll
    #     finalScroll += 1000
    #     sleep(rd.randint(2, 7))
    #     end = time()
    #     if round(end - start) > rd.randint(5, 9):
    #         break

    # num_scrolls = 10
    #
    # for _ in range(num_scrolls):
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     try:
    #         # Wait for a loading indicator to disappear (replace with the correct indicator if needed)
    #         WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.CLASS_NAME, 'loading-indicator')))
    #     except Exception:
    #         pass  # If the loading indicator doesn't appear, just continue scrolling
    #     sleep(2)

    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'org-people-profiles-card')))

    # Initialize variables for dynamic scrolling
    prev_page_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    # Scroll down the page to load more content dynamically
    # while True:
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #
    #     # Wait for a short time to allow content to load
    #     sleep(2)
    #
    #     # Get the current page height after the scroll
    #     curr_page_height = driver.execute_script("return document.body.scrollHeight")
    #
    #     if curr_page_height == prev_page_height:
    #         # If the page height hasn't changed, no more content is loading
    #         break
    #
    #     prev_page_height = curr_page_height
    #     scroll_attempts += 1

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            # Wait for a loading indicator to disappear (replace with the correct indicator if needed)
            WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.CLASS_NAME, 'loading-indicator')))
        except Exception:
            pass  # If the loading indicator doesn't appear, just continue scrolling
        sleep(2)
        curr_page_height = driver.execute_script("return document.body.scrollHeight")

        if curr_page_height == prev_page_height:
            # If the page height hasn't changed, no more content is loading
            break

        prev_page_height = curr_page_height
        scroll_attempts += 1

    search_ul = driver.find_element(By.XPATH, "//div[contains(@class, 'scaffold-finite-scroll__content')]/ul")

    search_li = search_ul.find_elements(By.XPATH, './/li')
    lt = []
    for li in search_li:
        a = []
        emp_info = str(li.text).split('\n')
        discard_info = ['3rd+ degree connection', '· 3rd', '2nd degree connection', '· 2nd', '1st degree connection', '· 1st', 'Connect']
        for i in emp_info:
            if i not in discard_info:
                a.append(i)

        try:
            a_tag = li.find_element(By.XPATH, ".//a")
            href_val = a_tag.get_attribute('href')
            a.append(href_val)
        except Exception as e:
            a.append('Not found')

        lt.append(a)
    

    print(lt)
    return lt