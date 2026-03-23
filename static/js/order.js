let orders = JSON.parse(localStorage.getItem('userOrders') || '[]');

function createOrder(orderData) {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    
    const newOrder = {
        id: 'ORD' + Date.now().toString().slice(-8),
        userId: userData.id || 'guest',
        customerName: userData.name || orderData.customerName,
        customerPhone: userData.phone || orderData.customerPhone,
        customerEmail: userData.email || orderData.customerEmail,
        customerType: userData.type || orderData.customerType || 'individual',
        companyName: orderData.companyName || '',
        governorate: orderData.governorate || '',
        address: orderData.address || '',
        products: orderData.products || [],
        quantity: orderData.quantity || 0,
        subtotal: orderData.subtotal || 0,
        deliveryFee: orderData.deliveryFee || 0,
        total: orderData.total || 0,
        paymentMethod: orderData.paymentMethod || 'cash_on_delivery',
        paymentStatus: 'pending',
        status: 'قيد المراجعة',
        deliveryDate: orderData.deliveryDate || '',
        deliveryTime: orderData.deliveryTime || '',
        notes: orderData.notes || '',
        assignedAgent: null,
        agentPhone: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    orders.unshift(newOrder);
    saveOrdersToStorage();
    
    return newOrder;
}

function getUserOrders(userId) {
    if (userId) {
        return orders.filter(order => order.userId === userId);
    }
    return orders;
}

function getOrderById(orderId) {
    return orders.find(order => order.id === orderId);
}

function updateOrderStatus(orderId, newStatus) {
    const order = getOrderById(orderId);
    
    if (order) {
        order.status = newStatus;
        order.updatedAt = new Date().toISOString();
        
        if (newStatus === 'في الطريق' && !order.assignedAgent) {
            order.assignedAgent = 'محمد أحمد';
            order.agentPhone = '01234567890';
        }
        
        saveOrdersToStorage();
        return order;
    }
    
    return null;
}

function deleteOrder(orderId) {
    const index = orders.findIndex(order => order.id === orderId);
    
    if (index !== -1) {
        const deletedOrder = orders.splice(index, 1);
        saveOrdersToStorage();
        return deletedOrder[0];
    }
    
    return null;
}

function saveOrdersToStorage() {
    localStorage.setItem('userOrders', JSON.stringify(orders));
}

function calculateOrderTotal(products, deliveryFee = 0) {
    const subtotal = products.reduce((total, item) => {
        return total + (item.price * item.quantity);
    }, 0);
    
    const total = subtotal + deliveryFee;
    
    return { subtotal, total };
}

function generateInvoice(order) {
    const invoice = {
        invoiceNumber: 'INV' + order.id.slice(-6),
        orderId: order.id,
        customerName: order.customerName,
        customerPhone: order.customerPhone,
        customerEmail: order.customerEmail,
        date: order.createdAt,
        items: order.products,
        subtotal: order.subtotal,
        deliveryFee: order.deliveryFee,
        total: order.total,
        paymentMethod: order.paymentMethod === 'cash_on_delivery' ? 'الدفع عند الاستلام' : 'الدفع الإلكتروني',
        status: order.status
    };
    
    return invoice;
}

function trackOrder(orderId) {
    const order = getOrderById(orderId);
    
    if (!order) {
        return { error: 'الطلب غير موجود' };
    }
    
    const trackingInfo = {
        orderId: order.id,
        status: order.status,
        currentStep: getOrderStep(order.status),
        steps: [
            { name: 'قيد المراجعة', completed: true, date: order.createdAt },
            { name: 'في الطريق', completed: order.status === 'في الطريق' || order.status === 'تم الاستلام' || order.status === 'مكتمل', date: order.updatedAt },
            { name: 'تم الاستلام', completed: order.status === 'تم الاستلام' || order.status === 'مكتمل', date: null },
            { name: 'مكتمل', completed: order.status === 'مكتمل', date: null }
        ],
        estimatedDelivery: order.deliveryDate,
        assignedAgent: order.assignedAgent,
        agentPhone: order.agentPhone
    };
    
    return trackingInfo;
}

function getOrderStep(status) {
    switch(status) {
        case 'قيد المراجعة': return 1;
        case 'في الطريق': return 2;
        case 'تم الاستلام': return 3;
        case 'مكتمل': return 4;
        default: return 1;
    }
}

function createSampleOrders() {
    if (orders.length === 0) {
        const sampleOrders = [
            {
                id: 'ORD2023001',
                userId: 'guest',
                customerName: 'أحمد محمد',
                customerPhone: '01234567890',
                customerEmail: 'ahmed@example.com',
                customerType: 'individual',
                governorate: 'القاهرة',
                address: 'شارع النصر، المهندسين',
                products: [
                    { id: 1, name: 'ورق كرتون مستعمل', price: 8.5, quantity: 20, unit: 'كجم', company_id: 1 }
                ],
                quantity: 20,
                subtotal: 170,
                deliveryFee: 20,
                total: 190,
                paymentMethod: 'cash_on_delivery',
                paymentStatus: 'paid',
                status: 'مكتمل',
                deliveryDate: '2023-10-15',
                deliveryTime: '14:00',
                assignedAgent: 'محمد أحمد',
                agentPhone: '01234567890',
                createdAt: '2023-10-14T10:30:00',
                updatedAt: '2023-10-15T14:30:00'
            },
            {
                id: 'ORD2023002',
                userId: 'guest',
                customerName: 'أحمد محمد',
                customerPhone: '01234567890',
                customerEmail: 'ahmed@example.com',
                customerType: 'individual',
                governorate: 'الجيزة',
                address: 'الدقي، شارع جامعة القاهرة',
                products: [
                    { id: 2, name: 'ورق مكتبي نظيف', price: 6.5, quantity: 15, unit: 'كجم', company_id: 1 },
                    { id: 3, name: 'جرائد ومجلات مستعملة', price: 4.0, quantity: 10, unit: 'كجم', company_id: 2 }
                ],
                quantity: 25,
                subtotal: 137.5,
                deliveryFee: 25,
                total: 162.5,
                paymentMethod: 'electronic',
                paymentStatus: 'paid',
                status: 'في الطريق',
                deliveryDate: '2023-10-20',
                deliveryTime: '10:00-14:00',
                assignedAgent: 'علي محمود',
                agentPhone: '01112223344',
                createdAt: '2023-10-18T09:15:00',
                updatedAt: '2023-10-19T11:20:00'
            }
        ];
        
        orders = sampleOrders;
        saveOrdersToStorage();
    }
}

createSampleOrders();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createOrder,
        getUserOrders,
        getOrderById,
        updateOrderStatus,
        deleteOrder,
        calculateOrderTotal,
        generateInvoice,
        trackOrder,
        orders
    };
}