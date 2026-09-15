import os
import django

def populate():
    from colleges.models import College, Stream

    colleges_data = [
        {
            'name': 'Maulana Abul Kalam Azad University of Tech (MAKAUT)',
            'slug': 'makaut-main',
            'uni': 'MAKAUT',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
                'CSE (AI/ML)',
            ]
        },
        {
            'name': 'JIS University',
            'slug': 'jis-uni',
            'uni': 'AUTONOMOUS',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
                'CSE (AI/ML)',
                'CSE (DS)',
            ]
        },
        {
            'name': 'Jadavpur University',
            'slug': 'ju',
            'uni': 'JU',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
            ]
        },
        {
            'name': 'Kalyani Government Engineering College',
            'slug': 'kgec',
            'uni': 'MAKAUT',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
            ]
        },
        {
            'name': 'Heritage Institute of Technology',
            'slug': 'hitk',
            'uni': 'AUTONOMOUS',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
                'Chemical Engineering',
            ]
        },
        {
            'name': 'Institute of Engineering and Management',
            'slug': 'iem',
            'uni': 'AUTONOMOUS',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
                'CSE (AI/ML)',
                'CSE (IoT)',
                'CSE (DS)',
                'Electrical and Electronics Engineering',
                'Biotechnology',

            ]
        },
        {
            'name': 'Techno Main Salt Lake',
            'slug': 'tiu',
            'uni': 'MAKAUT',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
                'Electrical and Electronics Engineering',
            ]
        },
        {
            'name': 'University of Calcutta',
            'slug': 'cu',
            'uni': 'CU',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
            ]
        },
        {
            'name': 'Adamas University',
            'slug': 'adamas',
            'uni': 'AUTONOMOUS',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',

            ]
        },
        {
            'name': 'Jalpaiguri Government Engineering College',
            'slug': 'jgec',
            'uni': 'MAKAUT',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
            ]
        },
        {
            'name': 'University of Engineering & Management',
            'slug': 'uem',
            'uni': 'AUTONOMOUS',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
                'CSE (AI/ML)',
                'CSE (IoT)',
                'CSE (DS)',
                'Electrical and Electronics Engineering',
                'Biotechnology',
            ]
        },
        {
            'name': 'Techno India University',
            'slug': 'techno',
            'uni': 'AUTONOMOUS',
            'streams': [
                'Computer Science & Engineering',
                'Information Technology',
                'Electronics & Communication Engineering',
                'Mechanical Engineering',
                'Civil Engineering',
                'Electrical Engineering',
            ]
        },
    ]

    for c_data in colleges_data:
        college, created = College.objects.get_or_create( # get_or_create -> If a college with the given slug already exists, it will return that college and created=False. If it doesn't exist, it will create a new college with the provided name and university, and return it with created=True.
            slug=c_data['slug'],# 
            defaults={'name': c_data['name'], 'university': c_data['uni']} # If a new college is created, it will use the name and university provided in defaults. If the college already exists, defaults will be ignored and the existing college's name and university will remain unchanged.
        )
        if created: # means : if college is created for the first time then print "Added: College Name"
            print(f" Added: {college.name}")
        else: # means : if college already exists in database then update its name and university with the latest data from colleges_data list, this is useful in case we want to change university name or correct any typo in college name later on, so we dont have to delete and re-add college again, just run this script and it will update existing records as well.
            college.name = c_data['name'] 
            college.university = c_data['uni']
            college.save()
            print(f" Updated: {college.name}") # means : if college already exists in database then print "Updated: College Name"

        for s_name in c_data['streams']: #
            _, s_created = Stream.objects.get_or_create(college=college, name=s_name)
            if s_created:
                print(f"   + {s_name}")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wb_papers.settings')
    django.setup()
    populate()
    from colleges.models import College, Stream
    print(f"\n Done! Colleges: {College.objects.count()}, Streams: {Stream.objects.count()}")