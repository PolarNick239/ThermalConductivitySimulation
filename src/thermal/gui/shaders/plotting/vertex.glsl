#line 1

in vec4 screen_position;

void main(void)
{
    vec4 world_position = to_world_mtx * screen_position;
    v2f.world_position = world_position.xy / world_position.w;
    gl_Position = screen_position;
}
