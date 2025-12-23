"""
Enhanced UI Styling Constants
Modern, interactive design with animations and effects
"""

# =============================================
# COLOR SCHEME - Modern & Vibrant
# =============================================

COLORS = {
    # Primary Colors - Gradient Blues
    'primary': '#667EEA',
    'primary_dark': '#5A67D8',
    'primary_light': '#7F9CF5',
    'primary_gradient_start': '#667EEA',
    'primary_gradient_end': '#764BA2',
    
    # Secondary Colors - Teal
    'secondary': '#38B2AC',
    'secondary_dark': '#319795',
    'secondary_light': '#4FD1C5',
    
    # Accent Colors - Orange/Coral
    'accent': '#ED8936',
    'accent_dark': '#DD6B20',
    'accent_light': '#F6AD55',
    
    # Background Colors
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F7FAFC',
    'bg_tertiary': '#EDF2F7',
    'bg_dark': '#1A202C',
    'bg_gradient_start': '#667EEA',
    'bg_gradient_end': '#764BA2',
    
    # Text Colors
    'text_primary': '#1A202C',
    'text_secondary': '#4A5568',
    'text_light': '#A0AEC0',
    'text_white': '#FFFFFF',
    'text_muted': '#718096',
    
    # Status Colors
    'success': '#48BB78',
    'success_light': '#9AE6B4',
    'warning': '#ECC94B',
    'warning_light': '#FAF089',
    'error': '#F56565',
    'error_light': '#FEB2B2',
    'info': '#4299E1',
    'info_light': '#90CDF4',
    
    # Border Colors
    'border': '#E2E8F0',
    'border_light': '#EDF2F7',
    'border_dark': '#CBD5E0',
    'border_focus': '#667EEA',
    
    # Card Colors
    'card_bg': '#FFFFFF',
    'card_hover': '#F7FAFC',
    'card_shadow': 'rgba(0,0,0,0.1)',
    
    # Input Colors
    'input_bg': '#EDF2F7',
    'input_border': '#E2E8F0',
    'input_focus': '#667EEA',
    
    # Sidebar
    'sidebar_bg': '#1A202C',
    'sidebar_hover': '#2D3748',
    'sidebar_active': '#667EEA',
    'sidebar_text': '#E2E8F0',
    
    # Chart Colors
    'chart_1': '#667EEA',
    'chart_2': '#48BB78',
    'chart_3': '#ED8936',
    'chart_4': '#F56565',
    'chart_5': '#9F7AEA',
    'chart_6': '#38B2AC',
    'chart_7': '#ECC94B',
    'chart_8': '#FC8181',
}

# Category Colors - Vibrant palette
CATEGORY_COLORS = {
    'Food & Dining': '#F56565',
    'Transportation': '#ED8936',
    'Shopping': '#48BB78',
    'Entertainment': '#9F7AEA',
    'Healthcare': '#ED64A6',
    'Education': '#4299E1',
    'Housing': '#667EEA',
    'Utilities': '#38B2AC',
    'Travel': '#F6AD55',
    'Gifts': '#B794F4',
    'Phone & Internet': '#63B3ED',
    'Other': '#A0AEC0',
}

# Chart color palette
CHART_COLORS = [
    '#667EEA', '#48BB78', '#ED8936', '#F56565', 
    '#9F7AEA', '#38B2AC', '#ECC94B', '#ED64A6',
    '#4299E1', '#F6AD55', '#68D391', '#FC8181'
]

# =============================================
# FONTS - Modern Typography
# =============================================

FONTS = {
    'heading_xl': ('Segoe UI', 32, 'bold'),
    'heading_large': ('Segoe UI', 28, 'bold'),
    'heading': ('Segoe UI', 24, 'bold'),
    'heading_small': ('Segoe UI', 20, 'bold'),
    'subheading': ('Segoe UI', 16, 'bold'),
    'body_large': ('Segoe UI', 14),
    'body': ('Segoe UI', 12),
    'body_medium': ('Segoe UI', 12, 'bold'),
    'body_small': ('Segoe UI', 10),
    'button': ('Segoe UI', 12, 'bold'),
    'button_large': ('Segoe UI', 14, 'bold'),
    'caption': ('Segoe UI', 9),
    'mono': ('Consolas', 11),
    'mono_large': ('Consolas', 14),
}

# =============================================
# DIMENSIONS
# =============================================

DIMENSIONS = {
    # Window
    'window_width': 1280,
    'window_height': 750,
    'min_width': 1100,
    'min_height': 650,
    
    # Sidebar
    'sidebar_width': 260,
    'sidebar_collapsed': 70,
    
    # Cards
    'card_padding': 24,
    'card_radius': 16,
    'card_shadow_blur': 20,
    
    # Buttons
    'button_height': 44,
    'button_radius': 10,
    'button_padding_x': 24,
    'button_padding_y': 12,
    
    # Inputs
    'input_height': 48,
    'input_radius': 10,
    'input_padding': 16,
    
    # Spacing
    'spacing_xs': 4,
    'spacing_sm': 8,
    'spacing_md': 16,
    'spacing_lg': 24,
    'spacing_xl': 32,
    'spacing_xxl': 48,
}

# =============================================
# BUTTON STYLES
# =============================================

BUTTON_STYLES = {
    'primary': {
        'bg': COLORS['primary'],
        'fg': COLORS['text_white'],
        'hover': COLORS['primary_dark'],
        'active': COLORS['primary_light'],
        'shadow': True,
    },
    'secondary': {
        'bg': COLORS['secondary'],
        'fg': COLORS['text_white'],
        'hover': COLORS['secondary_dark'],
        'active': COLORS['secondary_light'],
        'shadow': True,
    },
    'success': {
        'bg': COLORS['success'],
        'fg': COLORS['text_white'],
        'hover': '#38A169',
        'active': COLORS['success_light'],
        'shadow': True,
    },
    'outline': {
        'bg': COLORS['bg_primary'],
        'fg': COLORS['primary'],
        'hover': COLORS['bg_secondary'],
        'active': COLORS['bg_tertiary'],
        'border': COLORS['primary'],
    },
    'danger': {
        'bg': COLORS['error'],
        'fg': COLORS['text_white'],
        'hover': '#E53E3E',
        'active': COLORS['error_light'],
        'shadow': True,
    },
    'ghost': {
        'bg': 'transparent',
        'fg': COLORS['text_secondary'],
        'hover': COLORS['bg_secondary'],
        'active': COLORS['bg_tertiary'],
    },
    'gradient': {
        'bg': COLORS['primary'],
        'fg': COLORS['text_white'],
        'hover': COLORS['primary_dark'],
        'gradient': True,
    }
}

# =============================================
# ICON MAPPINGS (Enhanced)
# =============================================

ICONS = {
    # Navigation
    'dashboard': '🏠',
    'expenses': '💳',
    'add': '➕',
    'budget': '💰',
    'reports': '📊',
    'analytics': '📈',
    'settings': '⚙️',
    'logout': '🚪',
    
    # Actions
    'edit': '✏️',
    'delete': '🗑️',
    'save': '💾',
    'cancel': '❌',
    'search': '🔍',
    'filter': '🔽',
    'export': '📤',
    'import': '📥',
    'refresh': '🔄',
    
    # Status
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    
    # Categories
    'food': '🍔',
    'transport': '🚗',
    'shopping': '🛒',
    'entertainment': '🎬',
    'health': '💊',
    'education': '📚',
    'housing': '🏠',
    'utilities': '💡',
    'travel': '✈️',
    'gifts': '🎁',
    'phone': '📱',
    'other': '💼',
    
    # Misc
    'user': '👤',
    'calendar': '📅',
    'money': '💵',
    'category': '📁',
    'chart_pie': '🥧',
    'chart_bar': '📊',
    'chart_line': '📈',
    'wallet': '👛',
    'bank': '🏦',
    'card': '💳',
    'cash': '💵',
    'target': '🎯',
    'trophy': '🏆',
    'fire': '🔥',
    'star': '⭐',
    'bell': '🔔',
}

# =============================================
# MENU ITEMS (Enhanced)
# =============================================

MENU_ITEMS = [
    {'key': 'dashboard', 'label': 'Dashboard', 'icon': '🏠'},
    {'key': 'expenses', 'label': 'Expenses', 'icon': '💳'},
    {'key': 'add_expense', 'label': 'Add Expense', 'icon': '➕'},
    {'key': 'budget', 'label': 'Budget', 'icon': '🎯'},
    {'key': 'reports', 'label': 'Reports', 'icon': '📊'},
    {'key': 'analytics', 'label': 'Analytics', 'icon': '📈'},
]

# =============================================
# ANIMATION SETTINGS
# =============================================

ANIMATIONS = {
    'hover_duration': 150,
    'transition_duration': 200,
    'fade_duration': 300,
}

# =============================================
# GRADIENT DEFINITIONS
# =============================================

GRADIENTS = {
    'primary': ('#667EEA', '#764BA2'),
    'success': ('#48BB78', '#38A169'),
    'warning': ('#ECC94B', '#DD6B20'),
    'danger': ('#F56565', '#C53030'),
    'info': ('#4299E1', '#3182CE'),
    'purple': ('#9F7AEA', '#6B46C1'),
    'teal': ('#38B2AC', '#319795'),
    'orange': ('#ED8936', '#DD6B20'),
}
