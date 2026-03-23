const products = [
    {
        id: 1,
        name: "ورق كرتون مستعمل عالي الجودة",
        description: "كرتون نظيف وجاهز تماماً لإعادة التدوير والتصنيع. يستخدم في المصانع والورش والمشروعات التجارية. مناسب لكميات من 10 كجم فأكثر.",
        price: 8.5,
        unit: "كجم",
        image: "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        category: "كرتون",
        available: true,
        minQuantity: 10,
        company_id: 1,
        company_name: "شركة التدوير الأولى",
        features: [
            "جودة عالية",
            "جاهز للتدوير",
            "مناسب للمصانع",
            "كميات كبيرة"
        ]
    },
    {
        id: 2,
        name: "ورق مكتبي نظيف",
        description: "ورق مكتبي نظيف وخالي من المواد اللاصقة، مثالي لإعادة التدوير. يمكن استخدامه في صناعة الورق الجديد.",
        price: 6.5,
        unit: "كجم",
        image: "https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        category: "ورق مكتبي",
        available: true,
        minQuantity: 5,
        company_id: 1,
        company_name: "شركة التدوير الأولى",
        features: [
            "نظيف تماماً",
            "خالي من المواد اللاصقة",
            "مناسب للتدوير",
            "أسعار تنافسية"
        ]
    },
    {
        id: 3,
        name: "جرائد ومجلات مستعملة",
        description: "جرائد ومجلات مستعملة، مثالية لإعادة التدوير. تستخدم في صناعة الورق المقوى والمنتجات الورقية.",
        price: 4.0,
        unit: "كجم",
        image: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        category: "جرائد",
        available: true,
        minQuantity: 3,
        company_id: 2,
        company_name: "شركة الورق الأخضر",
        features: [
            "أسعار مناسبة",
            "متوفر بكثرة",
            "صديق للبيئة",
            "تدوير سهل"
        ]
    },
    {
        id: 4,
        name: "ورق كرتون مضلع",
        description: "كرتون مضلع عالي الجودة، مثالي للتغليف وإعادة الاستخدام. مناسب للمشاريع التجارية والصناعية.",
        price: 9.0,
        unit: "كجم",
        image: "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        category: "كرتون",
        available: true,
        minQuantity: 15,
        company_id: 2,
        company_name: "شركة الورق الأخضر",
        features: [
            "مضلع عالي الجودة",
            "ممتاز للتغليف",
            "يمكن إعادة الاستخدام",
            "مناسب للكميات الكبيرة"
        ]
    },
    {
        id: 5,
        name: "ورق أبيض نظيف",
        description: "ورق أبيض نظيف من المكاتب والمدارس، خالي من الكتابة والطباعة، جاهز لإعادة التدوير.",
        price: 7.0,
        unit: "كجم",
        image: "https://images.unsplash.com/photo-1565689221354-d87f85d4aee2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        category: "ورق أبيض",
        available: true,
        minQuantity: 5,
        company_id: 3,
        company_name: "شركة التدوير المتطورة",
        features: [
            "أبيض نظيف",
            "خالي من الكتابة",
            "جودة ممتازة",
            "سعر تنافسي"
        ]
    },
    {
        id: 6,
        name: "كرتون أرشيفي",
        description: "كرتون أرشيفي مستعمل، مناسب للمكتبات والمحفوظات. يمكن إعادة تدويره لصناعة منتجات ورقية جديدة.",
        price: 5.5,
        unit: "كجم",
        image: "https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        category: "كرتون",
        available: true,
        minQuantity: 8,
        company_id: 3,
        company_name: "شركة التدوير المتطورة",
        features: [
            "مناسب للأرشيف",
            "جودة متوسطة",
            "سعر اقتصادي",
            "متوفر بكميات"
        ]
    }
];

function getAllProducts() {
    return products;
}

function getProductById(id) {
    return products.find(product => product.id === id);
}

function getProductsByCategory(category) {
    return products.filter(product => product.category === category);
}

function getProductsByCompany(companyId) {
    return products.filter(product => product.company_id === companyId);
}

function searchProducts(query) {
    const searchTerm = query.toLowerCase();
    return products.filter(product => 
        product.name.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm) ||
        product.category.toLowerCase().includes(searchTerm)
    );
}

function createProduct(productData) {
    const newProduct = {
        id: products.length + 1,
        ...productData,
        created_at: new Date().toISOString()
    };
    
    products.push(newProduct);
    saveProductsToStorage();
    return newProduct;
}

function updateProduct(id, updatedData) {
    const index = products.findIndex(product => product.id === id);
    
    if (index !== -1) {
        products[index] = { ...products[index], ...updatedData };
        saveProductsToStorage();
        return products[index];
    }
    
    return null;
}

function deleteProduct(id) {
    const index = products.findIndex(product => product.id === id);
    
    if (index !== -1) {
        const deletedProduct = products.splice(index, 1);
        saveProductsToStorage();
        return deletedProduct[0];
    }
    
    return null;
}

function saveProductsToStorage() {
    localStorage.setItem('products', JSON.stringify(products));
}

function loadProductsFromStorage() {
    const storedProducts = JSON.parse(localStorage.getItem('products') || 'null');
    
    if (storedProducts) {
        products.length = 0;
        products.push(...storedProducts);
    }
}

// Load products from storage on initialization
loadProductsFromStorage();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getAllProducts,
        getProductById,
        getProductsByCategory,
        getProductsByCompany,
        searchProducts,
        createProduct,
        updateProduct,
        deleteProduct,
        products
    };
}