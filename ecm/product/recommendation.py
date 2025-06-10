# recommendation.py

from .models import productt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def get_similar_products_for_cart(cart_products, top_n=2):
    # Define manual product recommendations
    product_recommendations = {
        "bread": ["milk", "butter"],  # Bread is often bought with Milk and Butter
        "milk": ["bread", "butter"],  # Milk is often bought with Bread and Butter
        "butter": ["bread", "milk"],
        "oil" : ["rice"],
        "rice" : ["oil"] , # Butter is often bought with Bread and Milk
        # Add more manual relationships here
    }
    
    # Get all products from the database
    all_products = list(productt.objects.all())

    recommendations = set()
    cart_product_names = [product.pname.lower() for product in cart_products]

    # Iterate through each product in the cart and get the recommended products
    for product in cart_products:
        # Check if the product has any manual recommendations
        if product.pname.lower() in product_recommendations:
            for recommended_product in product_recommendations[product.pname.lower()]:
                # Find matching products not already in the cart
                for p in all_products:
                    if p.pname.lower() == recommended_product and p.pname.lower() not in cart_product_names:
                        recommendations.add(p)
                        if len(recommendations) >= top_n:
                            break
                if len(recommendations) >= top_n:
                    break
        if len(recommendations) >= top_n:
            break

    return list(recommendations)


# Category + Name/Brand Based Filtering (Smarter category recs)
def get_smart_category_recommendations(cart_products, per_product=2):
    all_products = list(productt.objects.all())
    cart_ids = [p.id for p in cart_products]
    recommendations = set()

    vectorizer = TfidfVectorizer()
    product_texts = [f"{p.pname} {p.pbrand}" for p in all_products]
    tfidf_matrix = vectorizer.fit_transform(product_texts)

    for cart_product in cart_products:
        same_category_products = [p for p in all_products if p.category == cart_product.category and p.id != cart_product.id]
        if not same_category_products:
            continue

        same_cat_indices = [i for i, p in enumerate(all_products) if p in same_category_products]
        cart_index = all_products.index(cart_product)

        sim_scores = cosine_similarity(tfidf_matrix[cart_index:cart_index+1], tfidf_matrix[same_cat_indices]).flatten()
        sorted_indices = np.argsort(sim_scores)[::-1]

        count = 0
        for i in sorted_indices:
            recommended_product = same_category_products[i]
            if recommended_product.id not in cart_ids:
                recommendations.add(recommended_product)
                count += 1
                if count >= per_product:
                    break

    return list(recommendations)
