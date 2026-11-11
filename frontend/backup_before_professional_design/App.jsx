import { useEffect, useState } from "react";
import "./App.css";

// Django backend address
const DJANGO_URL = "http://127.0.0.1:8000";

// Resolve Django image URLs
function getMediaUrl(path) {
    if (!path) return "";

    if (path.startsWith("http")) {
        return path;
    }

    return `${DJANGO_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}

// Resolve advertisement URLs
function getTargetUrl(url) {
    if (!url) return DJANGO_URL;

    if (url.startsWith("http")) {
        return url;
    }

    return `${DJANGO_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}


// HEADER
function Header() {

    return (

        <header className="header">

            {/* <a className="brand" href={`${DJANGO_URL}/`}>
                EGIS LEARNING
            </a> */}
<a className="brand" href="/">
    EGIS LEARNING
</a>
            <nav>

                <a href="#categories">
                    Categories
                </a>

                <a href="#courses">
                    Courses
                </a>

                <a href={`${DJANGO_URL}/admin/`}>
                    Admin
                </a>

                <a
                    className="button"
                    href={`${DJANGO_URL}/accounts/login/`}
                >
                    Log in
                </a>

                <a href={`${DJANGO_URL}/our-trainings/`}>
                    Our Trainings
                </a>

            </nav>

        </header>

    );

}


// HERO SECTION
function Hero() {

    return (

        <section className="hero">

            <h1>
                Learn new skills. Build your future.
            </h1>

            <p>
                Explore practical courses for beginners,
                intermediate learners, and advanced professionals.
                Preview a course and subscribe to unlock the
                full learning experience.
            </p>

            <a className="button" href="#courses">
                Explore Courses
            </a>

            <a
                className="button secondary-button"
                href={`${DJANGO_URL}/our-trainings/`}
            >
                Explore All Trainings →
            </a>

        </section>

    );

}


// ADVERTISEMENTS
function Advertisements({ advertisements }) {

    if (!advertisements || advertisements.length === 0) {
        return null;
    }

    return (

        <section className="advertisement-section">

            <div className="section-heading">

                <h2>
                    Promotions & Opportunities
                </h2>

                <p className="muted">
                    Discover exciting learning opportunities
                    and programmes.
                </p>

            </div>

            <div className="advertisement-grid">

                {advertisements.map((ad) => {

                    const imageUrl = getMediaUrl(ad.image);

                    const content = (

                        <>

                            <span className="advertisement-label">
                                ADVERTISEMENT
                            </span>

                            {ad.image && (

                                <img
                                    src={imageUrl}
                                    alt={ad.title || "EGIS advertisement"}
                                />

                            )}

                            {(ad.title || ad.description) && (

                                <div className="advertisement-content">

                                    <h3>
                                        {ad.title}
                                    </h3>

                                    <p>
                                        {ad.description}
                                    </p>

                                </div>

                            )}

                        </>

                    );

                    return (

                        <article
                            className="advertisement"
                            key={ad.id}
                        >

                            {ad.target_url ? (

                                <a
                                    href={getTargetUrl(ad.target_url)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    {content}
                                </a>

                            ) : content}

                        </article>

                    );

                })}

            </div>

        </section>

    );

}


// CATEGORIES
function Categories({ categories }) {

    return (

        <section id="categories">

            <div className="section-heading">

                <h2>
                    Explore Categories
                </h2>

                <p className="muted">
                    Find learning opportunities in your area
                    of interest.
                </p>

            </div>

            <div className="categories">

                {categories.length > 0 ? (

                    categories.map((category) => {

                        const imageUrl = getMediaUrl(category.image);

                        return (

                            <article
                                className="category"
                                key={category.id}
                            >

                                {category.image ? (

                                    <img
                                        src={imageUrl}
                                        alt={category.name}
                                    />

                                ) : (

                                    <div className="category-placeholder">
                                        {category.name}
                                    </div>

                                )}

                                <div className="category-content">

                                    <h3>
                                        {category.name}
                                    </h3>

                                    <p className="muted">
                                        {category.description ||
                                            "Explore courses in this category."}
                                    </p>

                                    <a
                                        className="button"
                                        href={`${DJANGO_URL}/our-trainings/category/${category.slug}/`}
                                    >
                                        View Courses →
                                    </a>

                                </div>

                            </article>

                        );

                    })

                ) : (

                    <p>
                        No categories available yet.
                    </p>

                )}

            </div>

        </section>

    );

}


// FEATURED COURSES
function FeaturedCourses({ courses }) {

    return (

        <section
            id="courses"
            className="courses-section"
        >

            <div className="section-heading">

                <h2>
                    Featured Courses
                </h2>

                <p className="muted">
                    Preview courses before choosing your subscription.
                </p>

            </div>

            <div className="courses">

                {courses.length > 0 ? (

                    courses.map((course) => {

                        const imageUrl = getMediaUrl(course.thumbnail);

                        return (

                            <article
                                className="course"
                                key={course.id}
                            >

                                {course.thumbnail ? (

                                    <img
                                        src={imageUrl}
                                        alt={course.title}
                                    />

                                ) : (

                                    <div className="course-placeholder">
                                        EGIS COURSE
                                    </div>

                                )}

                                <div className="course-content">

                                    <span className="level">
                                        {course.level}
                                    </span>

                                    <h3>
                                        {course.title}
                                    </h3>

                                    <p className="muted">
                                        {course.description}
                                    </p>

                                    <p className="muted">
                                        Category: {course.category_name}
                                    </p>

                                    <a
                                        className="preview"
                                        href={`${DJANGO_URL}/courses/${course.slug}/`}
                                    >
                                        View Course →
                                    </a>

                                </div>

                            </article>

                        );

                    })

                ) : (

                    <p>
                        No published courses available yet.
                    </p>

                )}

            </div>

        </section>

    );

}


// FOOTER
function Footer() {

    return (

        <footer>

            <p>
                © {new Date().getFullYear()} EGIS Learning.
                Learn at your own pace.
            </p>

        </footer>

    );

}


// MAIN HOMEPAGE
function Home() {

    const [data, setData] = useState({

        advertisements: [],
        categories: [],
        courses: []

    });

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    useEffect(() => {

        fetch("/api/homepage/")

            .then((response) => {

                if (!response.ok) {

                    throw new Error(
                        "Unable to load homepage information."
                    );

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

            .catch((error) => {

                console.error(error);

                setError(
                    "Unable to connect to the EGIS server."
                );

            })

            .finally(() => {

                setLoading(false);

            });

    }, []);


    return (

        <>

            <Header />

            <Hero />

            <main>

                {loading && (

                    <p className="loading">
                        Loading EGIS Learning...
                    </p>

                )}

                {error && (

                    <p className="error-message">
                        {error}
                    </p>

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

            <Footer />

        </>

    );

}


export default Home;