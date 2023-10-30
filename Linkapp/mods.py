# Module for storing reusable functions

# def subparts(data,target):
#     topics=['About','Experience','Education','Projects','Skills','Interests','People also viewed','You might like','Pages for you','Recommendations','People you may know']
#     subarr=[]
#     try:
#        ind=data.index(target)+1
#     except ValueError:
#         return ["**    Not Available    **"]
#     while True:
#         if data[ind] in topics or ind>len(data):
#             break
#         subarr.append(data[ind])
#         ind+=1
#     return subarr


# ==============Priya code====================

def subparts(data, target, info):
    person_topics = ['About', 'Experience', 'Education', 'Projects', 'Skills', 'Interests', 'People also viewed',
                     'You might like', 'Pages for you', 'Recommendations', 'People you may know']
    company_topics = ['Overview', 'Website', 'Industry', 'Company size', 'Headquarters', 'Founded', 'Specialties']
    subarr = []
    try:
        ind = data.index(target) + 1
    except ValueError:
        return ["**    Not Available    **"]

    topics = ''
    if info == 'person':
        topics = person_topics
    elif info == 'company':
        topics = company_topics

    print(len(data))
    while True:
        if ind >= len(data):
            print(ind, len(data))
            break
        if data[ind] in topics:
            break
        subarr.append(data[ind])
        print(ind, subarr)
        ind += 1
        print(ind)

    return subarr
