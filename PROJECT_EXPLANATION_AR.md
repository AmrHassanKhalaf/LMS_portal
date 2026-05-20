# شرح كامل لمشروع Student Management System

هذا الملف مخصص لتسليم وشرح مشروع مادة الـ Backend. الشرح مكتوب بالعربي، مع ترك المصطلحات التقنية الأفضل أن تظل بالإنجليزي مثل `Django`, `Model`, `View`, `Template`, `ORM`, `RBAC`, `GPA`, `API`, `Migration`.

---

## 1. فكرة المشروع

المشروع عبارة عن `Student Management System` أو نظام لإدارة الطلاب داخل مؤسسة تعليمية.

النظام لا يكتفي بتسجيل بيانات الطلاب فقط، لكنه يغطي دورة تعليمية كاملة:

- تسجيل ودخول المستخدمين.
- تقسيم الصلاحيات بين `Admin`, `Teacher`, و `Student`.
- إدارة الطلاب والمدرسين.
- إدارة `Subjects`, `Semesters`, `Courses`, و `Timetable`.
- تسجيل الطلاب في المواد.
- رفع `Materials` بواسطة المدرس.
- إنشاء `Assignments` و `Quizzes`.
- تسليم الواجبات من الطالب.
- تصحيح الواجبات من المدرس.
- حساب الدرجات و `GPA` على معيار 4.
- عرض `Transcript` للطالب.
- عرض `Gradebook` للمدرس.
- وجود `Admin Panel` داخل التطبيق ولوحة `Django Admin` لإدارة التفاصيل.

---

## 2. التقنيات المستخدمة

- `Python`: لغة البرمجة الأساسية.
- `Django`: إطار العمل المستخدم لبناء الـ Backend والـ Routing والـ Templates.
- `SQLite`: قاعدة بيانات محلية أثناء التطوير.
- `Django ORM`: للتعامل مع قاعدة البيانات باستخدام Python بدل كتابة SQL مباشرة.
- `Django Templates`: لبناء صفحات HTML ديناميكية.
- `Bootstrap 5`: لتنسيق الواجهة وجعلها Responsive.
- `django-crispy-forms` و `crispy-bootstrap5`: لتحسين عرض الـ Forms.
- `Django REST Framework`: لتجهيز API endpoints قابلة للتوسع.
- `Simple JWT`: لدعم `JWT Authentication` في الـ API.
- `WhiteNoise`: لخدمة ملفات `static files` في بيئات الإنتاج.
- `python-decouple`: لقراءة الإعدادات الحساسة من ملف `.env`.
- `WeasyPrint`: لتوليد PDF مثل الشهادات.

---

## 3. هيكل المشروع

```text
config/
apps/
templates/
static/
media/
manage.py
requirements.txt
.env
db.sqlite3
```

شرح أهم المجلدات:

- `config/`: إعدادات المشروع الأساسية مثل `settings.py`, `urls.py`, `wsgi.py`, و `asgi.py`.
- `apps/`: يحتوي تطبيقات Django المقسمة حسب وظيفة كل جزء في النظام.
- `templates/`: يحتوي كل ملفات HTML.
- `static/`: يحتوي CSS و JavaScript والصور الثابتة.
- `media/`: يحتوي الملفات التي يرفعها المستخدم مثل صور الطلاب، ملفات الواجبات، ومواد الكورسات.
- `db.sqlite3`: قاعدة بيانات التطوير الحالية.
- `requirements.txt`: قائمة المكتبات المطلوبة لتشغيل المشروع.

---

## 4. التطبيقات الداخلية Apps

المشروع مقسم إلى عدة Apps لتسهيل التنظيم والصيانة.

### 4.1 accounts

مسؤول عن:

- تسجيل الطلاب `Register`.
- تسجيل الدخول `Login`.
- تسجيل الخروج `Logout`.
- إنشاء حساب مدرس بواسطة الـ Admin.
- إدارة أدوار المستخدمين `Roles`.
- التحكم في الصلاحيات باستخدام `RBAC`.

أهم الملفات:

- `models.py`: يحتوي `Profile` المرتبط بـ Django `User`.
- `forms.py`: يحتوي Forms التسجيل، الدخول، إنشاء مدرس، وتعديل User من الـ Admin Panel.
- `views.py`: يحتوي login/register/create teacher/user management.
- `decorators.py`: يحتوي `admin_required`, `teacher_required`, `student_required`.
- `mixins.py`: يحتوي Mixins لاستخدامها مع `Class-Based Views`.

ملاحظة مهمة:

المشروع يستخدم Django `User` الجاهز بدل `Custom User Model`. وتم إضافة `Profile` بعلاقة `OneToOne` لتخزين الدور `role`.

---

### 4.2 students

مسؤول عن بيانات الطلاب ولوحات التحكم.

أهم الوظائف:

- إضافة طالب.
- عرض قائمة الطلاب.
- عرض تفاصيل طالب.
- تعديل وحذف طالب بواسطة الـ Admin.
- Student Dashboard.
- Admin Panel الرئيسي.
- البحث عن الطلاب.

أهم Model:

`Student`

ويحتوي على:

- `user`
- `admission_number`
- `first_name`
- `last_name`
- `email`
- `academic_level`
- `status`
- `image`
- `enrollment_date`

ملاحظات الصلاحيات:

- الـ Admin يقدر يشوف ويعدل كل الطلاب.
- المدرس يرى فقط الطلاب المسجلين في كورساته.
- الطالب يرى بياناته الأكاديمية فقط.

---

### 4.3 academics

مسؤول عن الجانب الأكاديمي للمشروع.

أهم Models:

- `Semester`: يمثل الفصل الدراسي.
- `Subject`: يمثل المادة بشكل عام مثل `CS101`.
- `Course`: يمثل طرح مادة في Semester معين مع Teacher معين.
- `Timetable`: يمثل جدول المحاضرات.
- `CourseMaterial`: ملفات أو روابط يرفعها المدرس لكورس معين.
- `SubjectBook`: كتب أو ملفات مرتبطة بمادة مباشرة.
- `StudentCurriculum`: المواد التي اختارها الطالب في خطته.

الفرق بين `Subject` و `Course`:

- `Subject` هو تعريف المادة نفسها، مثل: Data Structures.
- `Course` هو نسخة من المادة في ترم معين مع مدرس معين، مثل: Data Structures في Fall 2026 مع Dr. Ahmed.

هذا التصميم أفضل لأنه يسمح بتدريس نفس المادة في أكثر من ترم أو بواسطة أكثر من مدرس بدون تكرار بيانات المادة.

---

### 4.4 enrollments

مسؤول عن تسجيل الطلاب في الكورسات وحساب الأداء الأكاديمي.

أهم Models:

- `CourseEnrollment`: يربط Student مع Course.
- `AcademicRecord`: يخزن `cumulative_gpa` و `total_credits_earned`.

حقول مهمة في `CourseEnrollment`:

- `student`
- `course`
- `status`
- `overall_score`
- `final_grade`
- `is_flagged_weak`
- `weak_reason`

وظائف مهمة:

- حساب `overall_score`.
- تحويل النسبة إلى `letter grade`.
- تحديث `AcademicRecord`.
- حساب `GPA` على معيار 4.
- تمييز الطالب كـ `Weak Student` يدويًا بواسطة المدرس.

---

### 4.5 assessments

مسؤول عن الواجبات والاختبارات والدرجات.

أهم Models:

- `Assignment`: واجب أو مشروع مرتبط بكورس.
- `Submission`: تسليم الطالب للواجب.
- `Quiz`: اختبار مرتبط بكورس.
- `Question`: سؤال داخل اختبار.
- `Choice`: اختيار داخل سؤال.
- `QuizAttempt`: محاولة الطالب في اختبار.
- `SubjectQuiz`: اختبار مرتبط بمادة مباشرة.
- `SubjectQuizAttempt`: محاولة الطالب في Subject Quiz.

النظام يدعم:

- المدرس ينشئ Assignment.
- الطالب يسلم Assignment.
- المدرس يصحح Submission.
- الطالب يحل Quiz.
- Quiz يتصحح تلقائيًا.
- Subject Quiz يدخل في حساب الدرجة.
- الدرجة تظهر للمدرس والطالب.

---

### 4.6 communication

مسؤول عن التواصل داخل النظام.

أهم Models:

- `Announcement`: إعلان عام أو مرتبط بكورس.
- `Notification`: إشعار موجه لمستخدم معين.

---

### 4.7 api

مسؤول عن `API endpoints` باستخدام `Django REST Framework`.

هذا الجزء مفيد لو أردنا مستقبلاً ربط المشروع بـ:

- Mobile App.
- React Frontend.
- Next.js Frontend.
- External System.

---

## 5. نمط Django MVT

Django يستخدم نمط `MVT`:

- `Model`: يمثل الجداول والعلاقات في قاعدة البيانات.
- `View`: يستقبل request، ينفذ business logic، ويرجع response.
- `Template`: يعرض HTML للمستخدم.

مثال:

عند فتح صفحة `Teacher Dashboard`:

1. المتصفح يرسل request.
2. Django يمرره من `urls.py` إلى view المناسبة.
3. الـ View تجلب بيانات المدرس فقط من الـ Database.
4. يتم إرسال البيانات إلى Template.
5. Template يعرض صفحة HTML.

---

## 6. نظام الصلاحيات RBAC

`RBAC` اختصار لـ `Role-Based Access Control`.

الأدوار الموجودة:

- `Admin`
- `Teacher`
- `Student`

كل User له Profile يحتوي `role`.

الصلاحيات الأساسية:

### Admin

- إدارة المستخدمين.
- إنشاء المدرسين.
- إنشاء وتعديل الطلاب.
- إدارة Semesters.
- إدارة Subjects.
- إدارة Courses.
- إدارة Timetable.
- متابعة الدرجات والـ GPA.
- الوصول إلى `Django Admin`.
- رؤية النظام كامل.

### Teacher

- يرى كورساته فقط.
- يرى طلابه فقط.
- يرى جدول محاضراته فقط.
- يرفع Materials لكورساته فقط.
- ينشئ Assignments لكورساته فقط.
- ينشئ Quizzes لكورساته فقط.
- يصحح Submissions الخاصة بكورساته فقط.
- يرى Gradebook الخاص بكورساته فقط.
- يضيف Weak Student يدويًا.

### Student

- يختار المواد من Browse Subjects.
- يتم تسجيله مباشرة في Course الخاص بالمادة.
- يرى كورساته فقط.
- يرى Schedule الخاص به فقط.
- يرى Assignments و Quizzes الخاصة بكورساته فقط.
- يسلم Assignments.
- يحل Quizzes.
- يرى Transcript و GPA الخاص به فقط.

---

## 7. Admin Panel

تم بناء Admin Panel داخل التطبيق نفسه.

الـ Admin Panel يحتوي على:

- ملخص عدد الطلاب.
- عدد المدرسين.
- عدد الكورسات.
- عدد المواد.
- عدد Assignments و Quizzes.
- عدد Pending Grades.
- Average GPA.
- Current Semester.
- Shortcuts لإدارة أجزاء النظام.
- Recent Courses.
- Teachers list مع زر Edit.

أهم صفحات الإدارة:

- `Admin Dashboard`: لوحة التحكم الرئيسية.
- `Manage Users`: إدارة كل المستخدمين.
- `Edit User`: تعديل username, name, email, role, active status.
- `Student List`: إدارة الطلاب.
- `Create Teacher`: إنشاء مدرس.
- `Backend Admin`: الدخول إلى Django Admin.

كما تم تحسين Django Admin ليشمل:

- Course Materials.
- Subject Books.
- Student Curriculum.
- Timetable.
- Subject Quizzes.
- Subject Quiz Attempts.
- Course Enrollments مع score و grade و weak flag.

---

## 8. Teacher Dashboard

Teacher Dashboard تعرض:

- Active Courses.
- Total Students.
- Assignments.
- To Grade.
- Students & Enrolled Subjects.
- Needs Grading.
- Weak Students Focus.
- Quick actions لإدارة Assignments, Quizzes, Gradebook, Materials.

تم التأكد أن:

- المدرس يرى طلابه فقط.
- المدرس يرى المواد الخاصة به فقط.
- المدرس يرى الجدول الخاص به فقط.
- المدرس لا يستطيع فتح بيانات مدرس آخر بالـ URL.

---

## 9. Student Dashboard

Student Dashboard تعرض:

- Enrolled Courses.
- GPA.
- Total Credits.
- Upcoming Assignments.
- Open Quizzes.
- Recent Materials.
- Notifications.

الطالب يرى بياناته فقط بناءً على `request.user`.

---

## 10. نظام تسجيل الطالب في مادة

الطالب يدخل إلى `Browse Subjects`.

عند الضغط على `Add to My Curriculum`:

1. يتم إنشاء سجل في `StudentCurriculum`.
2. يتم البحث عن Course مرتبط بالمادة.
3. يتم إنشاء أو تحديث `CourseEnrollment`.
4. حالة التسجيل تصبح `ENROLLED`.
5. تظهر المادة في `My Curriculum`.
6. تظهر عند المدرس في Teacher Dashboard.

تم إلغاء فكرة `Admin Approval`، وبالتالي التسجيل يتم مباشرة.

---

## 11. Materials System

المدرس يستطيع رفع Materials للكورسات الخاصة به.

المادة قد تكون:

- File مثل PDF أو DOC.
- URL link مثل رابط فيديو أو مصدر خارجي.

الطالب يرى Materials الخاصة بالكورسات المسجل فيها فقط.

---

## 12. Assignments Workflow

خط سير الواجب:

1. Teacher ينشئ Assignment لكورس من كورساته.
2. Student يرى Assignment إذا كان مسجلاً في الكورس.
3. Student يرفع Submission.
4. Teacher يرى Submission في Needs Grading.
5. Teacher يدخل score و feedback.
6. النظام يحدث:
   - `Submission.score`
   - `CourseEnrollment.overall_score`
   - `CourseEnrollment.final_grade`
   - `AcademicRecord.cumulative_gpa`
   - `AcademicRecord.total_credits_earned`

---

## 13. Quizzes Workflow

خط سير الـ Quiz:

1. Teacher ينشئ Quiz.
2. Teacher يضيف Questions و Choices.
3. Student يحل Quiz.
4. النظام يصحح Quiz تلقائيًا.
5. يتم إنشاء `QuizAttempt`.
6. يتم تحديث الدرجة و GPA.

يدعم المشروع أيضًا `SubjectQuiz` المرتبط بالمادة مباشرة، ويتم إدخاله في حساب الدرجة.

---

## 14. نظام الدرجات GPA

النظام يحسب GPA على معيار 4.

خريطة الدرجات:

```text
A  = 4.0
A- = 3.7
B+ = 3.3
B  = 3.0
B- = 2.7
C+ = 2.3
C  = 2.0
C- = 1.7
D+ = 1.3
D  = 1.0
F  = 0.0
```

تحويل النسبة إلى Letter Grade:

```text
90 أو أكثر = A
80 إلى أقل من 90 = B
70 إلى أقل من 80 = C
60 إلى أقل من 70 = D
أقل من 60 = F
```

معادلة GPA:

```text
GPA = sum(grade_points * credits) / total_credits
```

النظام لا يحسب الواجب غير المصحح ضمن الدرجة حتى لا يظلم الطالب.

---

## 15. Gradebook

المدرس يرى Gradebook الخاص بكورساته فقط.

Gradebook يعرض:

- الطلاب المسجلين في الكورس.
- Overall Score.
- Letter Grade.
- Assignments.
- Submissions.
- Course Quizzes.
- Subject Quizzes.
- حالة الطالب إذا كان Weak Student.

المدرس يستطيع الدخول على طالب معين ومراجعة كل مكونات درجته.

---

## 16. My Transcript

الطالب يرى Transcript الخاص به فقط.

Transcript يعرض:

- Cumulative GPA.
- Total Credits.
- Course.
- Semester.
- Credits.
- Score.
- Letter Grade.

قبل عرض Transcript يتم تحديث الدرجات لضمان أن البيانات المعروضة حديثة.

---

## 17. Weak Students

النظام يدعم Weak Students بطريقتين:

1. Automatic:
   - إذا كانت `overall_score` أقل من 60.
2. Manual:
   - المدرس يستطيع عمل `Add Weak` لطالب معين مع كتابة سبب.

المدرس يستطيع إزالة الطالب من Weak Focus لاحقًا.

---

## 18. Timetable

`Timetable` يربط Course بموعد ومكان.

يحتوي على:

- Course.
- Day of week.
- Start time.
- End time.
- Room number.

الصلاحيات:

- Admin يرى Master Timetable.
- Teacher يرى My Schedule الخاص بكورساته فقط.
- Student يرى My Schedule الخاص بالكورسات المسجل فيها فقط.

---

## 19. API

يوجد App باسم `api` يستخدم `Django REST Framework`.

الـ API يوفر Serializers و ViewSets لبعض البيانات مثل:

- Students.
- Courses.
- Enrollments.

وجود API يجعل المشروع قابل للتطوير مستقبلًا لربطه بـ mobile app أو frontend منفصل.

---

## 20. Security

أهم نقاط الأمان في المشروع:

- كل صفحة حساسة محمية بـ Decorator أو Mixin.
- Role checks تتم على السيرفر وليس في الواجهة فقط.
- Teacher لا يرى إلا بياناته.
- Student لا يرى إلا بياناته.
- Admin فقط يستطيع تعديل المستخدمين والأدوار.
- Forms تمنع إدخال score أكبر من max score أو أقل من صفر.
- `.env` يستخدم لحفظ الإعدادات الحساسة.

---

## 21. Static و Media

`static/` يحتوي:

- CSS.
- JavaScript.
- صور ثابتة.

`media/` يحتوي:

- صور الطلاب.
- ملفات الواجبات.
- ملفات Materials.
- كتب المواد.

في Development يتم خدمة media files من خلال Django عندما يكون `DEBUG=True`.

---

## 22. أهم Routes

أمثلة على أهم الروابط:

```text
/accounts/login/
/accounts/register/
/accounts/create-teacher/
/accounts/admin-users/

/students/
/students/list/
/students/my-dashboard/

/academics/teacher-dashboard/
/academics/subjects/
/academics/my-curriculum/
/academics/timetable/
/academics/materials/

/assessments/assignments/manage/
/assessments/quizzes/manage/
/assessments/gradebook/
/assessments/my-transcript/

/admin/
```

---

## 23. تشغيل المشروع

تثبيت المكتبات:

```bash
pip install -r requirements.txt
```

تطبيق migrations:

```bash
python manage.py migrate
```

إنشاء Superuser:

```bash
python manage.py createsuperuser
```

تشغيل السيرفر:

```bash
python manage.py runserver
```

فتح المشروع:

```text
http://127.0.0.1:8000/
```

---

## 24. الفحوصات التي تمت

تم تشغيل:

```bash
python manage.py check
python -m ruff check .
python manage.py makemigrations --check --dry-run
```

كما تم عمل Smoke Tests على:

- Admin Panel.
- User Management.
- Teacher Dashboard.
- Browse Subjects.
- Student Enrollment.
- My Schedule لكل Role.
- Gradebook.
- Assignment grading.
- Quiz attempts.
- GPA calculation.
- Transcript.

---

## 25. أهم الإصلاحات والتحسينات

تم تنفيذ تحسينات كثيرة على المشروع، أهمها:

- إصلاح ربط الطالب بالمادة والـ CourseEnrollment.
- إلغاء Admin Approval للتسجيل في المادة.
- جعل Browse Subjects للمدرس يعرض مواده فقط.
- جعل Schedule لكل مدرس يعرض جدوله فقط.
- جعل الطلاب الظاهرين للمدرس هم طلاب كورساته فقط.
- إضافة Teacher Materials.
- إضافة Weak Student manual flag.
- إصلاح وربط الدرجات بالكامل.
- حساب GPA على معيار 4.
- إضافة Signals لتحديث الدرجات تلقائيًا بعد التصحيح أو الاختبار.
- إضافة Admin Panel احترافية داخل التطبيق.
- تحسين Django Admin.
- تحسين الصلاحيات ومنع الوصول للبيانات بالـ URL المباشر.

---

## 26. شرح مختصر للدكتور

المشروع عبارة عن Student Management System مبني بـ Django. النظام يطبق RBAC بثلاثة أدوار: Admin, Teacher, Student. الـ Admin يدير المستخدمين والطلاب والمدرسين والأكاديميات. المدرس يدير كورساته فقط من حيث الواجبات والاختبارات والمواد والدرجات. الطالب يسجل في المواد، يرى جدول محاضراته، يحل الاختبارات، يسلم الواجبات، ويتابع Transcript و GPA.

تم تصميم قاعدة البيانات بحيث يوجد فصل واضح بين Subject و Course و Semester، وهذا يجعل النظام قابل للتوسع. كما تم بناء نظام درجات يحسب overall score و letter grade و GPA تلقائيًا بناءً على Assignments و Quizzes و Subject Quizzes.

المشروع يستخدم Django ORM و Templates و Bootstrap، ويوجد به API قابل للتوسع باستخدام Django REST Framework. كما يحتوي على Admin Panel داخل التطبيق بالإضافة إلى Django Admin backend لإدارة البيانات التفصيلية.

---

## 27. مصطلحات مهمة

- `Backend`: الجزء المسؤول عن logic وقاعدة البيانات والـ server.
- `Frontend`: الواجهة التي يتعامل معها المستخدم.
- `Model`: تمثيل جدول في قاعدة البيانات.
- `View`: دالة أو Class تستقبل request وترجع response.
- `Template`: ملف HTML ديناميكي.
- `ORM`: طريقة للتعامل مع قاعدة البيانات باستخدام Python objects.
- `Migration`: ملف يصف تغييرات قاعدة البيانات.
- `RBAC`: نظام صلاحيات حسب الدور.
- `GPA`: المعدل التراكمي.
- `CourseEnrollment`: تسجيل طالب في Course.
- `Gradebook`: دفتر درجات المدرس.
- `Transcript`: كشف درجات الطالب.
- `API`: واجهة برمجية للتعامل مع النظام من تطبيق خارجي.
- `JWT`: طريقة Authentication تعتمد على Token.
- `Static Files`: ملفات CSS/JS/images الثابتة.
- `Media Files`: ملفات يرفعها المستخدم.

---

## 28. الخلاصة

المشروع منظم كتطبيق Django متعدد Apps، ويغطي معظم وظائف نظام إدارة أكاديمي حقيقي: users, roles, students, teachers, subjects, courses, schedule, materials, assignments, quizzes, grading, GPA, transcript, and admin management.

النقطة القوية في المشروع هي أن الصلاحيات ليست مجرد أزرار مخفية في الواجهة، بل موجودة في الـ Views نفسها. كذلك نظام الدرجات مرتبط فعليًا بين المدرس والطالب، بحيث أي تصحيح أو اختبار ينعكس على Gradebook و Transcript و GPA.

