const projects = [
    {
        title: "Customer Churn Prediction",
        description: "Developed a machine learning model to predict customer churn using Python and scikit-learn.  Achieved 92% accuracy in identifying customers at risk of leaving.",
        techStack: ["Python", "Pandas", "Scikit-learn", "Jupyter Notebook"],
        githubLink: "https://github.com/yourusername/churn-prediction",
        liveDemoLink: null,
        image: "https://placehold.co/600x400/EEE/31343C", // Placeholder
        features: [
            "Data Preprocessing and Feature Engineering",
            "Model Selection (Logistic Regression, Random Forest)",
            "Model Evaluation and Hyperparameter Tuning",
            "Visualization of Results"
        ]
    },
    {
        title: "Sales Forecasting with Time Series Analysis",
        description: "Implemented time series models (ARIMA, Prophet) to forecast future sales trends.  Improved forecast accuracy by 15% compared to the baseline model.",
        techStack: ["Python", "Pandas", "Prophet", "Matplotlib", "Seaborn"],
        githubLink: "https://github.com/yourusername/sales-forecasting",
        liveDemoLink: null,
        image: "https://placehold.co/600x400/EEE/31343C",
        features: [
            "Exploratory Data Analysis (EDA) of Time Series Data",
            "Stationarity Testing and Data Transformation",
            "Model Fitting and Validation",
            "Visualization of Forecasts and Confidence Intervals"
        ]
    },
    {
        title: "Sentiment Analysis of Social Media Data",
        description: "Built a natural language processing pipeline to analyze the sentiment of tweets related to a specific topic.  Deployed a Streamlit application to visualize real-time sentiment.",
        techStack: ["Python", "NLTK", "Transformers", "Streamlit"],
        githubLink: "https://github.com/yourusername/sentiment-analysis",
        liveDemoLink: "https://your-streamlit-app.herokuapp.com", // Replace
        image: "https://placehold.co/600x400/EEE/31343C",
        features: [
            "Text Preprocessing and Cleaning",
            "Sentiment Classification Using Pre-trained Models",
            "Real-time Data Collection and Analysis",
            "Interactive Visualization with Streamlit"
        ]
    },
    {
        title: "Image Classification with Convolutional Neural Networks",
        description: "Developed a CNN model using TensorFlow and Keras to classify images of different objects. Achieved 95% accuracy on the test set.",
        techStack: ["Python", "TensorFlow", "Keras", "OpenCV"],
        githubLink: "https://github.com/yourusername/image-classification",
        liveDemoLink: null,
        image: "https://placehold.co/600x400/EEE/31343C",
        features: [
            "Data augmentation and preprocessing",
            "CNN architecture design and training",
            "Model evaluation and visualization of results",
            "Integration with a web application for image upload and classification"
        ]
    },
    {
        title: "Customer Segmentation with Clustering",
        description: "Applied unsupervised learning techniques (K-Means, DBSCAN) to segment customers based on their purchasing behavior.  Identified key customer segments for targeted marketing campaigns.",
        techStack: ["Python", "Pandas", "Scikit-learn", "Matplotlib"],
        githubLink: "https://github.com/yourusername/customer-segmentation",
        liveDemoLink: null,
        image: "https://placehold.co/600x400/EEE/31343C",
        features: [
            "Data exploration and feature selection",
            "Clustering algorithm implementation and comparison",
            "Visualization of customer segments",
            "Interpretation of segment characteristics"
        ]
    },
    {
        title: "Fraud Detection with Machine Learning",
        description: "Built a machine learning model to detect fraudulent transactions in a financial dataset.  Reduced fraud by 80% while minimizing false positives.",
        techStack: ["Python", "Pandas", "Scikit-learn", "XGBoost"],
        githubLink: "https://github.com/yourusername/fraud-detection",
        liveDemoLink: null,
        image: "https://placehold.co/600x400/EEE/31343C",
        features: [
            "Handling imbalanced data",
            "Feature engineering and selection",
            "Model selection and evaluation (Logistic Regression, XGBoost)",
            "Performance metrics (Precision, Recall, F1-score, AUC-ROC)"
        ]
    },
];

function createProjectCard(project) {
    const card = document.createElement("div");
    card.className = "project-card";

    const image = document.createElement("img");
    image.src = project.image;
    image.alt = project.title;

    const cardContent = document.createElement("div");
    cardContent.className = "project-card-content";

    const title = document.createElement("h3");
    title.textContent = project.title;

    const description = document.createElement("p");
    description.className = "project-card-description";
    description.textContent = project.description;

    const techStack = document.createElement('p');
    techStack.classList.add('tech-stack');
    techStack.textContent = "Tech: " + project.techStack.join(', ');

    const featuresTitle = document.createElement("h4");
    featuresTitle.textContent = "Key Features:";
    featuresTitle.classList.add("font-semibold", "mt-4");

    const featuresList = document.createElement("ul");
    project.features.forEach(feature => {
        const li = document.createElement("li");
        li.textContent = feature;
        featuresList.appendChild(li);
    });

    const linksDiv = document.createElement("div");
    linksDiv.className = "links";

    if (project.githubLink) {
        const githubLink = document.createElement("a");
        githubLink.href = project.githubLink;
        githubLink.textContent = "GitHub";
        githubLink.classList.add("github");
        githubLink.target = "_blank";
        linksDiv.appendChild(githubLink);
    }

    if (project.liveDemoLink) {
        const demoLink = document.createElement("a");
        demoLink.href = project.liveDemoLink;
        demoLink.textContent = "Live Demo";
        demoLink.classList.add("demo");
        demoLink.target = "_blank";
        linksDiv.appendChild(demoLink);
    }

    cardContent.appendChild(title);
    cardContent.appendChild(description);
    cardContent.appendChild(techStack);
    if(project.features && project.features.length > 0){
        cardContent.appendChild(featuresTitle);
        cardContent.appendChild(featuresList);
    }
    cardContent.appendChild(linksDiv);

    card.appendChild(image);
    card.appendChild(cardContent);

    return card;
}

const projectsGrid = document.getElementById("projects-grid");
projects.forEach(project => {
    const card = createProjectCard(project);
    projectsGrid.appendChild(card);
});
</script>