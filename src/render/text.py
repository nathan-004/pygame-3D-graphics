import pygame 

def correct_text_placement(text: str, surface: pygame.Surface, font_size=24, color=(0, 0, 0), bg_color=None):
    """
    Affiche du texte sur une surface en le divisant en plusieurs lignes si nécessaire.
    
    Args:
        text: Le texte à afficher
        surface: La surface pygame où afficher le texte
        font_size: Taille de la police
        color: Couleur du texte (RGB)
        bg_color: Couleur de fond (None = transparent)
    
    Returns:
        La surface modifiée avec le texte
    """
    font = pygame.font.Font(None, font_size)
    surface_width = surface.get_width()
    surface_height = surface.get_height()
    
    # Diviser le texte en mots
    words = text.split(' ')
    lines = []
    current_line = ""
    
    # Construire les lignes en fonction de la largeur disponible
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_surface = font.render(test_line, True, color)
        
        if test_surface.get_width() > surface_width - 10:  # Laisser 10px de marge
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Le mot seul est trop long, le mettre sur sa propre ligne
                lines.append(word)
                current_line = ""
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)
    
    # Afficher les lignes sur la surface
    line_height = font.get_linesize()
    total_height = len(lines) * line_height
    
    # Commencer à afficher à partir du centre vertical
    y_start = (surface_height - total_height) // 2
    
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, color)
        x = (surface_width - line_surface.get_width()) // 2
        y = y_start + i * line_height
        surface.blit(line_surface, (x, y))