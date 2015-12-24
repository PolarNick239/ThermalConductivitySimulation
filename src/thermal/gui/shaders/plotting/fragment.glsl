#line 1

uniform sampler1D ys_tex;
uniform sampler2D colormap_tex;

layout(location=0) out vec4 out_color;

float mapToYRange(float y) {
    return (y - y_range.x) / (y_range.y - y_range.x);
}

void main(void)
{
    vec2 xy = v2f.world_position;
    float plot_y = mapToYRange(texture(ys_tex, xy.x).x);
    vec4 color = texture(colormap_tex, vec2(plot_y, 0.0f));
    float cur_y = mapToYRange(xy.y);
    out_color = color + (1.0 - color) * (clamp(pow(abs(cur_y - plot_y) / line_width, 0.1f), 0.0f, 1.0f));
}
