#line 1

in vec4 position;
in vec4 color;

void main(void)
{
    gl_Position = mvp_mtx * position;
    gl_Position /= gl_Position.w;
    v2f.color = color;
}
