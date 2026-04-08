"""
Test dataset for RAGAS evaluation.
50 questions across all intent categories with ground truth answers.
Uses real order IDs and seller IDs from the actual dataset.
"""

TEST_CASES = [
    # ── ORDER STATUS (10 questions) ────────────────────────────
    {
        "question": "Where is my order?",
        "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
        "expected_intent": "order_status",
        "ground_truth": "The order has been delivered. The system should provide the delivery date, payment details, and confirm successful delivery.",
    },
    {
        "question": "Can you check the status of my order?",
        "order_id": "203096f03d82e0dffbc41ebc2e2bcfb7",
        "expected_intent": "order_status",
        "ground_truth": "The order was delivered late. The system should acknowledge the delay, state how many days late it was, and provide the delivery details.",
    },
    {
        "question": "Has my order been shipped yet?",
        "order_id": "53cdb2fc8bc7dce0b6741e2150273451",
        "expected_intent": "order_status",
        "ground_truth": "The order has been delivered. The system should confirm delivery, provide the delivery date and order details.",
    },
    {
        "question": "I placed an order and want to know when it will arrive",
        "order_id": "fbf9ac61453ac646ce8ad9783d7d0af6",
        "expected_intent": "order_status",
        "ground_truth": "The order was delivered but late. The system should provide the estimated and actual delivery dates and explain the delay.",
    },
    {
        "question": "Track my package please",
        "order_id": "6ea2f835b4556291ffdc53fa0b3b95e8",
        "expected_intent": "order_status",
        "ground_truth": "The order was delivered late. The system should provide tracking information including estimated vs actual delivery dates.",
    },
    {
        "question": "What happened to my purchase?",
        "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
        "expected_intent": "order_status",
        "ground_truth": "The order has been successfully delivered. The system should confirm the delivery status and provide order details.",
    },
    {
        "question": "I want to know about my order status",
        "order_id": "",
        "expected_intent": "order_status",
        "ground_truth": "Without an order ID, the system should ask the customer to provide their order ID to look up the status.",
    },
    {
        "question": "When will my order be delivered?",
        "order_id": "",
        "expected_intent": "order_status",
        "ground_truth": "The system should ask the customer for their order ID to check expected delivery date.",
    },
    {
        "question": "I ordered something last week, is it on the way?",
        "order_id": "",
        "expected_intent": "order_status",
        "ground_truth": "Without an order ID, the system should request the order ID to check shipping status.",
    },
    {
        "question": "My order number is 203096f03d82e0dffbc41ebc2e2bcfb7, what is the status?",
        "order_id": "203096f03d82e0dffbc41ebc2e2bcfb7",
        "expected_intent": "order_status",
        "ground_truth": "The order was delivered but arrived late. The system should provide full delivery details and acknowledge the delay.",
    },

    # ── DELIVERY ISSUES (8 questions) ──────────────────────────
    {
        "question": "My order is late, it hasn't arrived yet",
        "order_id": "203096f03d82e0dffbc41ebc2e2bcfb7",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should acknowledge the delivery delay, provide the estimated vs actual delivery date, and offer a resolution or next steps.",
    },
    {
        "question": "My package never came",
        "order_id": "",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should empathize with the customer and ask for the order ID to investigate the delivery issue.",
    },
    {
        "question": "I've been waiting for weeks and still haven't received my order",
        "order_id": "fbf9ac61453ac646ce8ad9783d7d0af6",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should acknowledge the long wait, check the delivery status, and provide information about the delay with a resolution path.",
    },
    {
        "question": "The estimated delivery date has passed",
        "order_id": "6ea2f835b4556291ffdc53fa0b3b95e8",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should confirm that delivery is overdue, provide the original estimated date, and offer next steps such as contacting the seller or filing a complaint.",
    },
    {
        "question": "My parcel hasn't shown up",
        "order_id": "",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should ask for the order ID to look up delivery status and investigate the missing parcel.",
    },
    {
        "question": "Still waiting for my delivery, it's really overdue now",
        "order_id": "",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should empathize and request the order ID to check delivery status and delays.",
    },
    {
        "question": "delivery was supposed to arrive last week but nothing",
        "order_id": "203096f03d82e0dffbc41ebc2e2bcfb7",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should check the order details, confirm the delay, state the number of days late, and offer resolution options.",
    },
    {
        "question": "I never received my package, what do I do?",
        "order_id": "",
        "expected_intent": "delivery_issue",
        "ground_truth": "The system should guide the customer on next steps for undelivered packages and ask for the order ID to investigate.",
    },

    # ── REFUND REQUESTS (8 questions) ──────────────────────────
    {
        "question": "I want a refund for my order",
        "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
        "expected_intent": "refund_request",
        "ground_truth": "The system should check the order status and explain refund eligibility based on the return policy, including processing timeframes.",
    },
    {
        "question": "Can I get my money back?",
        "order_id": "",
        "expected_intent": "refund_request",
        "ground_truth": "The system should explain the refund policy and conditions for eligibility, and ask for order details.",
    },
    {
        "question": "I want to cancel my order and get a refund",
        "order_id": "203096f03d82e0dffbc41ebc2e2bcfb7",
        "expected_intent": "refund_request",
        "ground_truth": "The system should check the order status and explain cancellation/refund options based on current order state.",
    },
    {
        "question": "How do I request a refund?",
        "order_id": "",
        "expected_intent": "refund_request",
        "ground_truth": "The system should explain the refund request process, including steps to initiate a refund and the required conditions.",
    },
    {
        "question": "I need a reimbursement for the product I received",
        "order_id": "",
        "expected_intent": "refund_request",
        "ground_truth": "The system should explain refund eligibility criteria and ask for the order ID to proceed with the request.",
    },
    {
        "question": "This product was terrible, I want my money back",
        "order_id": "53cdb2fc8bc7dce0b6741e2150273451",
        "expected_intent": "refund_request",
        "ground_truth": "The system should empathize, check the order, explain refund/return options based on policy, and provide steps to initiate a return.",
    },
    {
        "question": "I'd like to return this and get a full refund",
        "order_id": "",
        "expected_intent": "refund_request",
        "ground_truth": "The system should explain the return and refund policy, including timeframes and eligibility conditions.",
    },
    {
        "question": "Can I do a chargeback on my order?",
        "order_id": "",
        "expected_intent": "refund_request",
        "ground_truth": "The system should explain the proper refund process through the platform before considering chargebacks, and outline the policy.",
    },

    # ── PRODUCT ISSUES (7 questions) ──────────────────────────
    {
        "question": "The product I received is broken",
        "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
        "expected_intent": "product_issue",
        "ground_truth": "The system should empathize, acknowledge the defective product report, and explain the return/replacement process per policy.",
    },
    {
        "question": "I got the wrong item in my order",
        "order_id": "",
        "expected_intent": "product_issue",
        "ground_truth": "The system should acknowledge the wrong item issue, ask for the order ID, and explain the resolution process.",
    },
    {
        "question": "The product is defective and not working at all",
        "order_id": "",
        "expected_intent": "product_issue",
        "ground_truth": "The system should empathize and explain the process for reporting defective products and getting a replacement or refund.",
    },
    {
        "question": "What I received is completely different from what was described",
        "order_id": "",
        "expected_intent": "product_issue",
        "ground_truth": "The system should acknowledge the mismatch, explain the consumer's rights, and outline the return/refund process for items not as described.",
    },
    {
        "question": "My item arrived damaged, the packaging was crushed",
        "order_id": "",
        "expected_intent": "product_issue",
        "ground_truth": "The system should empathize with the damaged delivery, and explain how to report damaged items and get a resolution.",
    },
    {
        "question": "Product has missing parts, it's incomplete",
        "order_id": "",
        "expected_intent": "product_issue",
        "ground_truth": "The system should acknowledge the incomplete product, and explain options for replacement or refund.",
    },
    {
        "question": "I think the product I received is counterfeit",
        "order_id": "",
        "expected_intent": "product_issue",
        "ground_truth": "The system should take the counterfeit report seriously, explain the platform's policy on authentic goods, and offer escalation options.",
    },

    # ── POLICY QUERIES (7 questions) ──────────────────────────
    {
        "question": "What is your return policy?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should explain the return policy including the return window, conditions for returns, and how to initiate a return.",
    },
    {
        "question": "How many days do I have to return a product?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should state the specific return window period and any conditions that apply to returns.",
    },
    {
        "question": "Am I eligible for a return on electronics?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should explain return eligibility for electronic products, including any special conditions or exceptions.",
    },
    {
        "question": "What are my consumer rights for defective products?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should explain consumer rights under Brazilian CDC (Consumer Defense Code) for defective products.",
    },
    {
        "question": "Can I return a used item?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should explain the policy on returning used or opened items, including any restrictions.",
    },
    {
        "question": "What happens if the seller doesn't respond to my complaint?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should explain the escalation process when sellers are unresponsive, including platform intervention timelines.",
    },
    {
        "question": "How long does a refund take to process?",
        "order_id": "",
        "expected_intent": "policy_query",
        "ground_truth": "The system should provide specific refund processing timeframes and any factors that affect the timeline.",
    },

    # ── SELLER ISSUES (5 questions) ────────────────────────────
    {
        "question": "I have a problem with this seller, they are not responding",
        "order_id": "0015a82c2db000af6aaaf3ae2ecb0532",
        "expected_intent": "seller_issue",
        "ground_truth": "The system should look up the seller data, show their performance metrics, and advise on escalation options for unresponsive sellers.",
    },
    {
        "question": "This seller sent me a fake product",
        "order_id": "001e6ad469a905060d959994f1b41e4f",
        "expected_intent": "seller_issue",
        "ground_truth": "The system should check the seller's metrics and complaint rate, acknowledge the concern, and explain how to report fraudulent sellers.",
    },
    {
        "question": "The vendor keeps delaying my shipment",
        "order_id": "00fc707aaaad2d31347cf883cd2dfe10",
        "expected_intent": "seller_issue",
        "ground_truth": "The system should check the seller's late delivery rate and provide information on the seller's performance and escalation options.",
    },
    {
        "question": "How do I report a bad seller?",
        "order_id": "",
        "expected_intent": "seller_issue",
        "ground_truth": "The system should explain the process for reporting seller issues and what actions the platform can take.",
    },
    {
        "question": "The merchant won't honor the return",
        "order_id": "",
        "expected_intent": "seller_issue",
        "ground_truth": "The system should explain the buyer's rights and the escalation process when a seller refuses to accept a return.",
    },

    # ── GENERAL / EDGE CASES (5 questions) ─────────────────────
    {
        "question": "Hello, I need help with something",
        "order_id": "",
        "expected_intent": "general",
        "ground_truth": "The system should greet the customer and ask how it can help, offering example topics like orders, returns, or policies.",
    },
    {
        "question": "Thank you for your help",
        "order_id": "",
        "expected_intent": "general",
        "ground_truth": "The system should respond politely, acknowledge the thanks, and offer further assistance if needed.",
    },
    {
        "question": "Can you help me with my problem?",
        "order_id": "",
        "expected_intent": "general",
        "ground_truth": "The system should ask the customer to describe their issue so it can provide relevant support.",
    },
    {
        "question": "I love this platform, keep up the great work",
        "order_id": "",
        "expected_intent": "general",
        "ground_truth": "The system should thank the customer for the positive feedback and offer any additional assistance.",
    },
    {
        "question": "What payment methods do you accept?",
        "order_id": "",
        "expected_intent": "general",
        "ground_truth": "The system should provide information about accepted payment methods based on available knowledge.",
    },
]
