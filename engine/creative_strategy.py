def generate_creative_strategy(diagnosis):
    strategies = {
        'Hook / creative problem': {
            'angles': [
                'Problem-solution angle',
                'Price shock angle',
                'POV relatable angle',
                'Comparison angle'
            ],
            'hooks': [
                'Still paying too much for this?',
                'Nobody tells you this before buying...',
                'This changed everything for me.',
                'Stop scrolling if you struggle with this.'
            ]
        },
        'Landing page speed or mismatch problem': {
            'angles': [
                'Fast delivery angle',
                'Simple shopping experience angle',
                'Trust & clarity angle'
            ],
            'hooks': [
                'From click to checkout in seconds.',
                'No confusing pages. Just results.',
                'Built for the fastest buying experience.'
            ]
        },
        'Product page or offer problem': {
            'angles': [
                'Offer stacking angle',
                'Bundle angle',
                'Value for money angle'
            ],
            'hooks': [
                'Get more without paying more.',
                'Why buy one when you can save on two?',
                'This offer beats every competitor.'
            ]
        },
        'Checkout or trust problem': {
            'angles': [
                'Social proof angle',
                'Guarantee angle',
                'Cash on delivery angle'
            ],
            'hooks': [
                'Trusted by thousands of customers.',
                'Risk-free shopping starts here.',
                'Order today and pay on delivery.'
            ]
        },
        'Creative fatigue detected': {
            'angles': [
                'New UGC angle',
                'Before/after angle',
                'Lifestyle angle'
            ],
            'hooks': [
                'New version. Better results.',
                'Watch this before buying.',
                'This is why everyone is switching.'
            ]
        },
        'Scaling-ready winner': {
            'angles': [
                'Winning angle expansion',
                'Authority angle',
                'High demand angle'
            ],
            'hooks': [
                'One of our top-selling products.',
                'The ad everyone keeps buying from.',
                'Demand is growing fast.'
            ]
        }
    }

    return strategies.get(diagnosis, {})
