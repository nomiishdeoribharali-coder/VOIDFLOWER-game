import pygame


class BloomEffect:
    def __init__(self, width, height, quality=0.5, threshold=80, intensity=1.0):
        self.width = width
        self.height = height
        self.quality = quality
        self.small_w = max(1, int(width * quality))
        self.small_h = max(1, int(height * quality))
        self.threshold = threshold
        self.intensity = intensity
        self.enabled = True

    def apply(self, surface):
        if not self.enabled:
            return surface

        small = pygame.transform.smoothscale(surface, (self.small_w, self.small_h))

        bright = pygame.Surface((self.small_w, self.small_h), pygame.SRCALPHA)
        for y in range(self.small_h):
            for x in range(self.small_w):
                try:
                    c = small.get_at((x, y))
                    brightness = (c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11)
                    if brightness > self.threshold:
                        factor = (brightness - self.threshold) / (255 - self.threshold)
                        factor = min(1.0, factor * 1.5)
                        r = min(255, int(c[0] * factor))
                        g = min(255, int(c[1] * factor))
                        b = min(255, int(c[2] * factor))
                        bright.set_at((x, y), (r, g, b, int(180 * factor)))
                except:
                    pass

        blurred = pygame.transform.smoothscale(bright, (self.width, self.height))
        blurred = pygame.transform.smoothscale(blurred, (self.small_w, self.small_h))
        blurred = pygame.transform.smoothscale(blurred, (self.width, self.height))

        if self.intensity != 1.0:
            intensity_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            intensity_surf.blit(blurred, (0, 0))
            blurred = intensity_surf
            blurred.set_alpha(min(255, int(255 * self.intensity)))

        result = surface.copy()
        result.blit(blurred, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return result
