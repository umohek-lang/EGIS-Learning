import { useEffect, useState } from "react";
import "./App.css";

// const DJANGO_URL = "http://127.0.0.1:8000";
// const DJANGO_URL = "http://10.168.80.141:8000";
const DJANGO_URL = (
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

// function getMediaUrl(path) {
//     if (!path) return "";

//     if (path.startsWith("http")) return path;

//     return path.startsWith("/") ? path : `/${path}`;
// }

function getMediaUrl(path) {
    if (!path) return "";

    if (path.startsWith("http")) return path;

    return `${DJANGO_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

function getTargetUrl(url) {
    if (!url) return DJANGO_URL;

    if (url.startsWith("http")) return url;

    return `${DJANGO_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}


// =========================================
// NAVIGATION
// =========================================

function Header() {

    const [menuOpen, setMenuOpen] = useState(false);

    return (

        <header className="header">

            <div className="header-container">

                <a href="/" className="brand">

                    <span className="brand-icon">E</span>

                    <span>
                        EGIS<span className="brand-gold">LEARNING</span>
                        <small>KNOWLEDGE FOR YOUR FUTURE</small>
                    </span>

                </a>

                <button
                    className="mobile-menu-button"
                    onClick={() => setMenuOpen(!menuOpen)}
                    aria-label="Toggle navigation"
                    aria-expanded={menuOpen}
                >
                    ☰
                </button>

                <nav className={menuOpen ? "nav-open" : ""}>

                    <a href="/" onClick={() => setMenuOpen(false)}>
                        Home
                    </a>

                    <a href="#categories" onClick={() => setMenuOpen(false)}>
                        Categories
                    </a>

                    <a href="#courses" onClick={() => setMenuOpen(false)}>
                        Courses
                    </a>

                    <a href="#about" onClick={() => setMenuOpen(false)}>
                        About Us
                    </a>

                    <a href="#contact" onClick={() => setMenuOpen(false)}>
                        Contact
                    </a>

                    <a
                        className="nav-login"
                        href={`${DJANGO_URL}/accounts/login/`}
                    >
                        Log In
                    </a>

                    <a
                        className="nav-register"
                        href={`${DJANGO_URL}/accounts/register/`}
                    >
                        Get Started
                    </a>

                </nav>

            </div>

        </header>

    );
}


// =========================================
// HERO SECTION
// =========================================

function Hero() {

    return (

        <section className="hero">

            <div className="hero-background-circle circle-one"></div>
            <div className="hero-background-circle circle-two"></div>

            <div className="hero-container">

                <div className="hero-content">

                    <span className="hero-label">
                        ✦ EMPOWERING MINDS. DEVELOPING SKILLS. SHAPING FUTURES.
                    </span>

                    <h1>
                        Transform Your Knowledge.
                        <span> Advance Your Future.</span>
                    </h1>

                    <p>
                        Take control of your personal and professional development
                        with industry-relevant courses, practical learning experiences
                        and expertly structured training programmes. Acquire valuable
                        skills, expand your capabilities and position yourself for
                        greater opportunities in an increasingly competitive world.
                    </p>

                    <div className="hero-buttons">

                        <a href="#courses" className="primary-button">
                            Explore Our Courses <span>→</span>
                        </a>

                        <a
                            href={`${DJANGO_URL}/accounts/register/`}
                            className="hero-secondary-button"
                        >
                            Join EGIS Learning
                        </a>

                    </div>

                    <div className="hero-trust">

                        <div>
                            <strong>Practical Education</strong>
                            <small>Knowledge translated into real-world skills</small>
                        </div>

                        <div>
                            <strong>Flexible Learning</strong>
                            <small>Learning designed around your schedule</small>
                        </div>

                        <div>
                            <strong>Career Advancement</strong>
                            <small>Develop capabilities for professional growth</small>
                        </div>

                    </div>

                </div>

                <div className="hero-visual">

                    <div className="hero-image-card">

                        <div className="hero-image-icon">✦</div>

                        <span className="image-caption">
                            INVEST IN YOUR POTENTIAL
                        </span>

                        <h2>
                            Every great achievement begins with the decision to learn.
                        </h2>

                        <div className="image-gold-line"></div>

                        <p>LEARN. DEVELOP. EXCEL.</p>

                    </div>

                    <div className="floating-card floating-top">
                        <span>✦</span>
                        Discover New Possibilities
                    </div>

                    <div className="floating-card floating-bottom">
                        <span>✓</span>
                        Build a Better Future
                    </div>

                </div>

            </div>

        </section>

    );
}


// =========================================
// TRUST SECTION
// =========================================

function TrustSection() {

    return (

        <section className="trust-section">

            <div className="trust-item">
                <strong>Practical Training</strong>
                <span>Acquire skills for real-world application</span>
            </div>

            <div className="trust-item">
                <strong>Experienced Instructors</strong>
                <span>Benefit from structured professional guidance</span>
            </div>

            <div className="trust-item">
                <strong>Flexible Learning</strong>
                <span>Study at a time and pace that suits you</span>
            </div>

            <div className="trust-item">
                <strong>Learning Certificates</strong>
                <span>Demonstrate your learning achievements</span>
            </div>

        </section>

    );
}


// =========================================
// SECTION HEADING
// =========================================

function SectionHeading({ label, title, description }) {

    return (

        <div className="section-heading">

            <span className="section-label">{label}</span>

            <h2>{title}</h2>

            <p>{description}</p>

        </div>

    );
}


// =========================================
// ADVERTISEMENTS
// =========================================

function Advertisements({ advertisements }) {

    if (!advertisements.length) return null;

    return (

        <section className="advertisement-section">

            <SectionHeading
                label="FEATURED ANNOUNCEMENTS"
                title="Opportunities Worth Exploring"
                description="Stay informed about our latest programmes, special announcements and learning opportunities designed to support your educational and professional development."
            />

            <div className="advertisement-grid">

                {advertisements.map((ad) => (

                    <article className="advertisement" key={ad.id}>

                        <a
                            href={`${DJANGO_URL}/advertisements/${ad.id}/`}
                            className="advertisement-link"
                        >

                            {ad.image && (

                                <img
                                    src={getMediaUrl(ad.image)}
                                    alt={ad.title || "EGIS Learning advertisement"}
                                />

                            )}

                            <div className="advertisement-content">

                                <span>FEATURED ANNOUNCEMENT</span>

                                <h3>{ad.title}</h3>

                                <p>{ad.description}</p>

                                <strong>Read More →</strong>

                            </div>

                        </a>

                    </article>

                ))}

            </div>

        </section>

    );
}

// =========================================
// CATEGORIES
// =========================================

function Categories({ categories }) {

    return (

        <section id="categories" className="categories-section">

            <SectionHeading
                label="EXPLORE OUR ACADEMIC OFFERINGS"
                title="Discover Learning Opportunities"
                description="Explore our diverse range of learning categories, carefully organised to help you identify relevant areas of interest, acquire valuable competencies and pursue your personal and professional ambitions."
            />

            <div className="categories-grid">

                {categories.length > 0 ? (

                    categories.map((category, index) => (

                        <a
                            href={`${DJANGO_URL}/our-trainings/category/${category.slug}/`}
                            className="category-card"
                            key={category.id}
                        >

                            {category.image ? (

                                <img
                                    src={getMediaUrl(category.image)}
                                    alt={category.name}
                                />

                            ) : (

                                <div className="category-icon">
                                    {["✦", "⌘", "◈", "◎", "✧", "◇"][index % 6]}
                                </div>

                            )}

                            <div className="category-info">

                                <h3>{category.name}</h3>

                                <p>
                                    {category.description ||
                                        "Explore structured learning programmes designed to strengthen your knowledge, develop relevant competencies and expand your professional capabilities."}
                                </p>

                                <span>Explore Category →</span>

                            </div>

                        </a>

                    ))

                ) : (

                    <p>
                        Our learning categories are currently being updated.
                        Please check back soon for available programmes.
                    </p>

                )}

            </div>

        </section>

    );
}


// =========================================
// FEATURED COURSES
// =========================================

function FeaturedCourses({ courses }) {

    return (

        <section id="courses" className="courses-section">

            <SectionHeading
                label="DEVELOP YOUR EXPERTISE"
                title="Explore Our Featured Courses"
                description="Access carefully structured courses that combine essential knowledge with practical learning. Build relevant competencies, strengthen your professional profile and prepare yourself for emerging opportunities."
            />

            <div className="courses-grid">

                {courses.length > 0 ? (

                    courses.map((course) => (

                        <article className="course-card" key={course.id}>

                            <a
                                href={`${DJANGO_URL}/courses/${course.slug}/`}
                                className="course-image"
                            >

                                {course.thumbnail ? (

                                    <img
                                        src={getMediaUrl(course.thumbnail)}
                                        alt={course.title}
                                    />

                                ) : (

                                    <div className="course-placeholder">
                                        EGIS LEARNING
                                    </div>

                                )}

                                <span className="course-level">
                                    {course.level}
                                </span>

                            </a>

                            <div className="course-content">

                                <span className="course-category">
                                    {course.category_name}
                                </span>

                                <h3>{course.title}</h3>

                                <p>
                                    {course.description}
                                </p>

                                <div className="course-footer">

                                    <span>
                                        Flexible, self-paced learning
                                    </span>

                                    <a href={`${DJANGO_URL}/courses/${course.slug}/`}>
                                        View Course →
                                    </a>

                                </div>

                            </div>

                        </article>

                    ))

                ) : (

                    <p>
                        There are currently no published courses available.
                        New learning programmes will be announced here.
                    </p>

                )}

            </div>

            <div className="all-courses-button">

                <a
                    href={`${DJANGO_URL}/our-trainings/`}
                    className="outline-button"
                >
                    Discover All Courses →
                </a>

            </div>

        </section>

    );
}


// =========================================
// WHY CHOOSE EGIS
// =========================================

function WhyChooseEgIs() {

    const benefits = [

        {
            icon: "01",
            title: "Application-Focused Learning",
            description: "Develop practical competencies through structured lessons, relevant examples and learning activities designed to connect knowledge with real-world application."
        },

        {
            icon: "02",
            title: "Learning on Your Schedule",
            description: "Enjoy the flexibility to access your subscribed learning materials at your convenience and progress through your studies at a pace that suits your commitments."
        },

        {
            icon: "03",
            title: "Personal and Professional Growth",
            description: "Strengthen your knowledge, broaden your capabilities and develop skills that support career advancement, workplace effectiveness and lifelong learning."
        },

        {
            icon: "04",
            title: "Measurable Learning Progress",
            description: "Monitor your learning journey, follow your course progress and earn certificates upon successfully meeting the applicable course completion requirements."
        }

    ];

    return (

        <section id="about" className="why-section">

            <div className="why-container">

                <div className="why-intro">

                    <span className="section-label">
                        THE EGIS LEARNING ADVANTAGE
                    </span>

                    <h2>
                        Building knowledge. Developing capabilities. Creating opportunities.
                    </h2>

                    <p>
                        At EGIS Learning, we recognise education as a powerful
                        foundation for personal transformation and professional
                        advancement. Our commitment is to make meaningful learning
                        opportunities accessible through structured courses,
                        practical instruction and flexible digital learning.

                        Whether you are developing new competencies, strengthening
                        existing knowledge or preparing for the next stage of your
                        career, EGIS Learning provides an environment where you can
                        continue to learn, grow and pursue excellence.
                    </p>

                    <a
                        href={`${DJANGO_URL}/accounts/register/`}
                        className="primary-button"
                    >
                        Become a Learner →
                    </a>

                </div>

                <div className="benefits-grid">

                    {benefits.map((benefit) => (

                        <article className="benefit-card" key={benefit.icon}>

                            <span>{benefit.icon}</span>

                            <h3>{benefit.title}</h3>

                            <p>{benefit.description}</p>

                        </article>

                    ))}

                </div>

            </div>

        </section>

    );
}


// =========================================
// CALL TO ACTION
// =========================================

function CallToAction() {

    return (

        <section className="cta-section">

            <div>

                <span>YOUR FUTURE DESERVES AN INVESTMENT</span>

                <h2>
                    Take the Next Step Towards Your Goals.
                </h2>

                <p>
                    Your ambitions deserve more than intention; they deserve
                    action. Join EGIS Learning, explore relevant learning
                    opportunities and begin developing the knowledge and
                    competencies that can move your future forward.
                </p>

                <a
                    href={`${DJANGO_URL}/accounts/register/`}
                    className="cta-button"
                >
                    Create Your Account →
                </a>

            </div>

        </section>

    );
}


// =========================================
// FOOTER
// =========================================

function Footer() {

    return (

        <footer id="contact" className="footer">

            <div className="footer-container">

                <div className="footer-brand">

                    <a href="/" className="brand footer-logo">

                        <span className="brand-icon">E</span>

                        <span>
                            EGIS<span className="brand-gold">LEARNING</span>
                            <small>KNOWLEDGE FOR YOUR FUTURE</small>
                        </span>

                    </a>

                    <p>
                        EGIS Learning is committed to advancing knowledge,
                        strengthening practical competencies and promoting
                        continuous personal and professional development
                        through accessible digital education.

                        We believe that learning is a lifelong investment
                        and that the right knowledge can create meaningful
                        opportunities for individuals and communities.
                    </p>

                </div>

                <div className="footer-links">

                    <h3>Explore EGIS</h3>

                    <a href="/">Home</a>

                    <a href="#categories">Learning Categories</a>

                    <a href="#courses">Featured Courses</a>

                    <a href="#about">About EGIS</a>

                </div>

                <div className="footer-links">

                    <h3>Learner Account</h3>

                    <a href={`${DJANGO_URL}/accounts/login/`}>
                        Sign In
                    </a>

                    <a href={`${DJANGO_URL}/accounts/register/`}>
                        Create an Account
                    </a>

                    <a href={`${DJANGO_URL}/accounts/dashboard/`}>
                        Learner Dashboard
                    </a>

                </div>

                <div className="footer-links">

                    <h3>Our Programmes</h3>

                    <a href={`${DJANGO_URL}/our-trainings/`}>
                        All Training Programmes
                    </a>

                    <a href="#courses">
                        Featured Learning Courses
                    </a>

                </div>

            </div>

            <div className="footer-bottom">

                <p>
                    © {new Date().getFullYear()} EGIS Learning.
                    All rights reserved.
                </p>

                <span>Learn. Develop. Excel.</span>

            </div>

        </footer>

    );

}


// =========================================
// MAIN HOMEPAGE
// =========================================

function Home() {

    const [data, setData] = useState({
        advertisements: [],
        categories: [],
        courses: []
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {

        const controller = new AbortController();

        // fetch("/api/homepage/", {
        //     signal: controller.signal
        // })

        fetch(`${DJANGO_URL}/api/homepage/`, {
    signal: controller.signal
})
            .then((response) => {

                if (!response.ok) {
                    throw new Error("Unable to load homepage information.");
                }

                return response.json();

            })

            .then((result) => {

                setData({
                    advertisements: result.advertisements || [],
                    categories: result.categories || [],
                    courses: result.courses || []
                });

            })

            .catch((err) => {

                if (err.name !== "AbortError") {

                    console.error(err);

                    setError(
                        "We are temporarily unable to retrieve the learning content. Please refresh the page or try again shortly."
                    );

                }

            })

            .finally(() => {

                if (!controller.signal.aborted) {
                    setLoading(false);
                }

            });

        return () => controller.abort();

    }, []);

    return (

        <>

            <Header />

            <Hero />

            <TrustSection />

            <main className="main-content">

                {loading && (

                    <div className="loading-state">

                        <div className="spinner"></div>

                        <p>
                            Loading learning opportunities and preparing
                            your educational experience...
                        </p>

                    </div>

                )}

                {error && (

                    <div className="error-message">
                        {error}
                    </div>

                )}

                <Advertisements
                    advertisements={data.advertisements}
                />

                <Categories
                    categories={data.categories}
                />

                <FeaturedCourses
                    courses={data.courses}
                />

            </main>

            <WhyChooseEgIs />

            <CallToAction />

            <Footer />

        </>

    );

}


export default Home;